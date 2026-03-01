#!/usr/bin/env bash

set -x
find c101 -name '*.ipynb' | while read nb
do
  py="${nb%.*}.py"
  sed -E -i.bak -e 's~^( *"execution_count":)[^,]*(.*)~\1 null\2~' "$nb"
  chmod u+w "$py" || :
  jupyter nbconvert --to script "$nb"
  chmod -w "$py"
done
