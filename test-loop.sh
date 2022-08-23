#!/bin/bash

watch_dirs=("src")

inotifywait -e close_write,moved_to,create,delete,moved_from -r -m "${watch_dirs[@]}" |
while read -r directory events filename; do
  # echo  "${filename}"
  if [[ "${filename}" =~ pyc ]]; then
    # echo '  - skip -'
    continue
  fi
  ./test.sh
  echo '======================================================================'
done
