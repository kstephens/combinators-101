#!/usr/bin/env bash

set -x
find c101 -name '*.ipynb' | while read nb
do
  sed -E -i.bak -e 's~^( *"execution_count":)[^,]*(.*)~\1 null\2~' "$nb"
  jupyter nbconvert --to script "$nb"
done
