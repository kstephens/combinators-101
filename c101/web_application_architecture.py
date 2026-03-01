#!/usr/bin/env python
# coding: utf-8

# # (Imports)

# In[ ]:


import sys; sys.path.append('..')
from c101.helpers import *


# # Web Application Architecture
# 
# Application middleware combinators inspired Python WSGI and Ruby Rack.
# 
# - An "App" is anything callable with a single dict argument.
# - It receives a "Request"
#   - typically a Dict of input: headers, body and customary values passed along an "application stack".
# - It returns an HTTP "Response": Tuple of:
#   - numeric HTTP status code
#   - dict of HTTP headers
#   - body -- a sequence of response body chunks
# - applications and middleware follow the same protocol.
# - Combinators create new Apps by wrapping others.
# 

# In[ ]:


# Types for a Web Application Stack:
Status = int
Headers = Dict[str, Any]
Body = Iterable[bytes | str]
Req = Dict[str, Any]
Res = Tuple[Status, Headers, Body]
App = Callable[[Req], Res]


# ## Simple Applications

# In[ ]:


def hello_world_app(req: Req) -> Res:
  return 200, {}, ["Hello, World!\n"]
app = hello_world_app
app({})


# ### Do Something Useful

# In[ ]:


def something_useful_app(req: Req) -> Res:
  x, y = req['req.data']
  return 200, {}, (x * y,)

app = something_useful_app
app({'req.data': [2, 5]})


# In[ ]:


app = something_useful_app
app({'req.data': ["ab", 3]})


# ## Application Combinators

# Input combinators follow this pattern:

# In[ ]:


def compose_input_handler(app: App) -> App:
  def input_handler(req: Req) -> Res:
    # do something with req...
    return app(req)
  return input_handler


# Output combinators follow this pattern:

# In[ ]:


def compose_output_handler(app: App) -> App:
  def output_handler(req: Req) -> Res:
    status, headers, body = response = app(req)  # <<<
    # do something with response...
    return status, headers, body
  return output_handler


# ## App Stack Tracing

# In[ ]:


app = something_useful_app
app = trace(app)
app({'req.data': [5, 7]})


# In[ ]:


# Composition Naming
def compname(g, name, *args):
    args = [a.__qualname__ if callable(a) else repr(a) for a in args]
    g.__qualname__ = f"{g}({','.join(args)})"
    return g


# In[ ]:


def app_comp(app: App, *stack) -> App:
    "Compose application stack."
    app = trace(app)
    for middleware in stack:
        app = trace(compname(middleware(app), middleware.__qualname__, app))
    return app


# ## Exception Handling

# In[ ]:


def capture_exception(app: App, cls=Exception, status=500) -> App:
    def capturing_exception(req: Req) -> Res:
        try:
            return app(req)
        except cls as exc:
            return status, {"Content-Type": "text/plain"}, (repr(exc),)
    return capturing_exception


# In[ ]:


app = something_useful_app
app = capture_exception(app)
app({'req.data': [{"a": 1}, 7]})


# ## Reading Inputs, Writing Outputs

# In[ ]:


Content = str
Data = Any

def read_input(app: App) -> App:
    "Reads req.stream"
    def reader(req: Req) -> Res:
        # TODO: check inbound Content-Length
        req["req.content"] = req["req.stream"].read()
        req["Content-Length"] = len(req["req.content"])
        return app(req)
    return reader


# ## Decoding Inputs, Encoding Outputs

# In[ ]:


Encoder = Callable[[Data], Content]
Decoder = Callable[[Content], Data]

def decode_content(app: App, decoder: Decoder, content_types=None, strict=False) -> App:
    """
    Decodes body with decoder(input.content) for content_types.
    If strict and Content-Type is not expected, return 400.
    """

    def decoding_content(req: Req) -> Res:
        req["req.data"] = decoder(req["req.content"])
        content_type = req.get("Content-Type")
        if strict and content_types and content_type not in content_types:
            msg = f"Unexpected Content-Type {content_type!r} : expected: {content_types!r} : "
            return 400, {"Content-Type": 'text/plain'}, (msg,)
        return app(req)
    return decoding_content


def encode_content(app: App, encoder: Encoder, content_type="text/plain") -> App:
    "Encodes body with encoder.  Sets Content-Type."
    def encoding_content(req: Req) -> Res:
        status, headers, body = app(req)
        content = "".join(map(encoder, body))
        headers |= {
            "Content-Type": content_type,
            "Content-Length": len(content),
        }
        return status, headers, [content]
    return encoding_content


# ## Decode JSON, Encode JSON

# In[ ]:


import json

def decode_json(app: App, **kwargs) -> App:
    "Decodes JSON content."
    def decoding_json(data: Data) -> Any:
        return json.loads(data, **kwargs)
    return decode_content(app, decoding_json, content_types={'application/json', 'text/plain'}, strict=True)


def encode_json(app: App, **kwargs) -> App:
    "Encodes data as JSON."
    def encoding_json(data: Data) -> Content:
        return json.dumps(data, **kwargs) + "\n"
    return encode_content(app, encoding_json, content_type='application/json')


# ## HTTP Protocol

# In[ ]:


def http_request(app: App) -> App:
    def http_req(req):
        req_io = req["req.stream"]
        request_method, path_info, server_protocol = req_io.readline().split(" ", 3)
        req = {}
        while line := req_io.readline().rstrip():
            k, v = line.strip().split(":", 2)
            req[k] = v.strip()
        req.update({
            "REQUEST_METHOD": request_method,
            "PATH_INFO": path_info,
            "SERVER_PROTOCOL": server_protocol,
            "req.stream": req_io,
            # "output.stream": res_io,
        })
        return app(req)
    return http_req

def http_response(app: App) -> App:
    def http_res(req):
        status, headers, body = app(req)
        res_io = req['res.stream']
        res_io.write(f"HTTP/1.1 {status} ...\n")
        for k, v in headers.items():
            res_io.write(f"{k}: {v}\n")
        res_io.write("\n")
        for chunk in body:
            if callable(chunk):
                chunk(res_io)
            res_io.write(chunk)
    return http_res

req_str = """\
POST / HTTP/1.1
Host: hello.world.com
Accept: */*
Content-Type: text/plain

Are you there?
"""
req_io = StringIO(req_str)
res_io = sys.stdout # StringIO()
app = app_comp(hello_world_app, http_request, http_response)
req = {"req.stream": req_io, "res.stream": res_io}
app(req)


# ## Simple App Handles JSON!

# In[ ]:


app = app_comp(something_useful_app, decode_json, encode_json, read_input, capture_exception, http_request, http_response)
req_str = """\
POST / HTTP/1.1
Host: hello.world.com
Accept: */*
Content-Type: application/json

[2, 3]
"""
req_io = StringIO(req_str)
res_io = sys.stdout # StringIO()
req = {"req.stream": req_io, "res.stream": res_io}
app(req)


# ----
# # The End
# ----
