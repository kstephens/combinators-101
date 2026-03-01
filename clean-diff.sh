#!/usr/bin/env bash

set -x
sed -E -e 's~^( *"execution_count":)[^,]*~\1: null,~' -i combinators-101.ipynb
