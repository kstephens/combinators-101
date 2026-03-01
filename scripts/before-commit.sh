#!/usr/bin/env bash

set -x
find c101 -name '*.ipynb' | while read nb
do
  py="${nb%.*}.py"
  html="${nb%.*}.html"
  html_dst="html/$html"

  jupyter nbconvert \
    --execute \
    --to html \
    --template lab \
    --HTMLExporter.theme=dark \
    "$nb"

  mkdir -p "${html_dst%/*}"
  chmod u+w "$html_dst" || :
  mv "$html" "$html_dst"
  chmod -w "$html"

  chmod u+w "$py" || :
  jupyter nbconvert --to script "$nb"
  python -m py_compile "$nb" || exit $?
  chmod -w "$py"

  nb_bak="$nb.bak"
  sed -E -i.bak -e 's~^( *"execution_count.":)[^,]*(.*)~\1 null\2~' "$nb"
  if ! jq -e < "$nb" >/dev/null
  then
    mv "$nb_bak" "$nb"
    exit 9
  else
    rm -f "$nb_bak"
  fi
done
