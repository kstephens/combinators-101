#!/usr/bin/env bash

set -x
find c101 -name '*.ipynb' | while read nb
do
  py="${nb%.*}.py"

  nb_bak="$nb.bak"
  sed -E -i.bak -e 's~^( *"execution_count.":)[^,]*(.*)~\1 null\2~' "$nb"
  jq -e < "$nb" >/dev/null || exit $?

  chmod u+w "$py" || :
  jupyter nbconvert --to script "$nb"
  if not python -m py_compile "$nb"
  then
    mv "$nb_bak" "$nb"
    exit 9
  else
    rm -f "$nb_bak"
  fi
  chmod -w "$py"
done
