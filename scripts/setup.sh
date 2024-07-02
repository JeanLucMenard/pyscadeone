#!/bin/bash
# Initialize a python virtual environment and add "flit" to it
#
# Usage: scripts/setup.sh <venv path> <python path>
#
# Must be run from scripts' parent dir

VENV=${1?"Missing venv path"}
PYTHON=${2?"Missing python path"}

venv_setup () {
    # Create virtual environment
    [ -d "$VENV" ] && return 0
    py_version=$("$PYTHON" -V 2>&1)
    read -p "Use $py_version [y/n]:"
    [ "$REPLY" != "y" ] && return 1
    read -p "Use $VENV env [y/n]:"
    [ "$REPLY" != "y" ] && return 1
    echo "Creating virtual environment $VENV"
    "$PYTHON" -m venv $VENV
    source scripts/activate.sh $VENV
    echo "pip upgrade"
    python -m pip install --upgrade pip 
    echo "flit install"
    pip install flit
}


venv_setup
if [ $? -ne 0 ]
then
    echo "use: make PYTHON=<python path> [VENV=<subfolder>] setup"
    exit 1 
fi
