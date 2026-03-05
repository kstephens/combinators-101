#!/usr/bin/env bash

get-ipynb-files() {
find c101 -name '*.ipynb' |
sort |
(
  echo c101/combinators_101.ipynb
  cat
)
}
set-vars() {
  py="${nb%.*}.py"
  html="${nb%.*}.html"
  html_dst="html/$html"
  nb_bak="$nb.bak"
}
ipynb-to-py() {
  chmod u+w "$py" || :
  jupyter nbconvert --to script "$nb"
  python -m py_compile "$nb" || exit $?
  chmod -w "$py"
}
ipynb-to-html() {
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
}
clean-up-ipynb() {
  sed -E -i.bak -e 's~^( *"execution_count.":)[^,]*(.*)~\1 null\2~' "$nb"
  if ! jq -e < "$nb" >/dev/null
  then
    mv "$nb_bak" "$nb"
    exit 9
  else
    rm -f "$nb_bak"
  fi
}
set -x

get-ipynb-files |
while read nb
do
  set-vars
  clean-up-ipynb
done

get-ipynb-files |
while read nb
do
  set-vars
  ipynb-to-py
done

get-ipynb-files |
while read nb
do
  set-vars
  ipynb-to-html
done

