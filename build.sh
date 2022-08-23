#!/bin/bash
set -e
set -x
rm -r dist/
_ve/bin/python -m build
