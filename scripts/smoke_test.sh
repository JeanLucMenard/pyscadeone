#!/bin/bash
# Perform smoke tests
#
# Usage: scripts/smoke_test.sh <venv path> <distrib>
#
# Must be run from scripts' parent dir	

VENV=${1?"Missing venv argument"}
DISTRIB=${2?"Missing distrib arg"}

if [ ! -f dist/${DISTRIB}*.whl ]
then
    echo "*** Missing distribution: dist/${DISTRIB}*.whl"
    exit 1
fi

echo "--- Setting smoke test environment"
# get python from environment
source scripts/activate.sh $VENV
SMOKE_PYTHON=$(type -fp python)
deactivate

SMOKE_ENV=smoke_env

# create a specific venv, answering yes
yes | make VENV=$SMOKE_ENV PYTHON="$SMOKE_PYTHON" _venv

# use the smoke test env
source scripts/activate.sh $SMOKE_ENV

# install the distibution
pip install dist/${DISTRIB}*.whl
echo "--- Running smoke test"
python tests/smoketest.py
[ $? -eq 0 ] && rm -rf $SMOKE_ENV

