#!/bin/bash
__DIR="$( cd "$( readlink -f $(dirname "${BASH_SOURCE[0]}" ))" && pwd )"
cd ${__DIR}
docker build -t scadgen .
