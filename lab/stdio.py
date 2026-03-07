import sys

stdio_stack = []


def stdio_save():
    stdio_stack.append((sys.stdin, sys.stdout, sys.stderr))


def stdio_silence():
    sys.stdout = sys.stderr = open("/dev/null", "w", encoding="utf-8")


def stdio_restore():
    assert stdio_stack
    sys.stdin, sys.stdout, sys.stderr = stdio_stack.pop()
