#!/bin/bash
set -e

# _ve/bin/python -m foo.bar.widget_test
_ve/bin/nose2
_ve/bin/pytype scadgen
