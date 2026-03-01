#!/usr/bin/env bash

set -x
python3.13 -m venv venv
. venv/bin/activate
pip install -r requirements.txt

