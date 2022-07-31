#!/bin/bash
__DIR="$( cd "$( readlink -f $(dirname "${BASH_SOURCE[0]}" ))" && pwd )"

if [ -z "$1" ]; then
  ve_dir="${__DIR}/_ve"
else
  ve_dir="${1}"
fi

if [ ! -d "${ve_dir}" ]; then
  virtualenv -p "$(which python3)" "${ve_dir}"
fi

"${ve_dir}/bin/pip" install --upgrade -r "${__DIR}/requirements.txt"
"${ve_dir}/bin/pip" install --upgrade -r "${__DIR}/requirements-dev.txt"

