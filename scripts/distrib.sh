#!/bin/bash
# Create a distribution, containing the .whl and the html documentation
# as a .zip.
# The distrib argument is the basename of the distrib, part of the wheel name.
#
# Usage: scripts/distrib.sh <venv path> <distrib>
#
# Must be run from scripts' parent dir

VENV=${1?"Missing venv path"}
DISTRIB=${2?"Missing distrib arg"}

ZIP=${DISTRIB}.zip

# Clean up
rm -rf dist/$DISTRIB dist/$ZIP
mkdir dist/$DISTRIB

# Copy data
cp dist/${DISTRIB}*.whl dist/$DISTRIB;
cp -r doc/_build/html dist/$DISTRIB/${DISTRIB}_html

# Zip
source scripts/activate.sh $VENV
cd dist
python -m zipfile -c $ZIP $DISTRIB

# end
rm -rf dist/$DISTRIB
echo "Distribution: ./dist/${DISTRIB}.zip"