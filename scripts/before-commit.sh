#!/usr/bin/env bash

set -x
for nb in *.ipynb
do
  sed -E -i.bak -e 's~^( *"execution_count":)[^,]*(.*)~\1 null\2~' "$nb"
  jupyter nbconvert --to script "$nb"
done
