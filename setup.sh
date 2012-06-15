#!/usr/bin/env bash
#
# Created by Samvel Khalatyan, Jun 14, 2012
# Copyright 2012, All rights reserved

python -c "import sys,os; sys.exit(0 if '$PWD' in os.getenv('PYTHONPATH').split(':') else 1)"
if [[ 0 == $? ]]
then
    echo "environment is set"
else
    echo "setup the environment"

    if [[ "" != "${PYTHONPATH}" ]]
    then
        export PYTHONPATH="$PWD:${PYTHONPATH}"
    else
        export PYTHONPATH="$PWD"
    fi
fi
