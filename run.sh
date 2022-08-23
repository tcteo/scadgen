#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${DIR}"

cmd="$1"
shift || true
if [ -z "${cmd}" ]; then
  echo 'no command'
  exit 1
fi

case "${cmd}" in

  "ve")
    ./ve.sh
    ;;

  "test")
    ./test.sh
    ;;
  
  "test-loop")
    ./test-loop.sh
    ;;

  "build")
    rm -rf dist/
    _ve/bin/python -m build
    ;;

  "docker-build")
    docker build -t scadgen .
    ;;

  "publish-test")
    _ve/bin/poetry publish -r testpypi
    ;;

  "publish")
    _ve/bin/poetry publish --build
    ;;

  *)
    echo "unknown command ${cmd}"
    exit 1
    ;;
esac
