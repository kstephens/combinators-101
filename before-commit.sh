#!/usr/bin/env bash

set -x
sed -E -i.bak -e 's~^( *"execution_count":)[^,]*(.*)~\1 null\2~' combinators-101.ipynb
jupyter nbconvert --to script combinators-101.ipynb
