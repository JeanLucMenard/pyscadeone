#!/bin/sh
# Script to run pytest with proper options
# Other pytest settings are in pyproject.toml

NAME=$(basename $0)
USAGE="Usage: $NAME [-h | OPTIONS]"

if [ "x$1" = "x" -o "x$1" = "x-h" ]
then
    [ "x$1" = "x" ] && echo $USAGE && exit 0 
    cat <<HELP
NAME
    $NAME

SYNOPSIS
    $NAME [OPTION]

DESCRIPTION
    Launch tests on scadeone module. Usage:

    $ ./$NAME
    or
    $ sh ./$NAME

    Options:

    -tests
        launch pytest on tests directory. Logs for python code
        is saved in logs/pytest-logs.txt

    -cov
        launch pytest on tests directory with -cov option.
        Reports are saved in htmlcov folder.

SEE ALSO
    pyproject.toml: contains pytest settings

HELP
    exit 0

elif [ "x$1" = "x-tests" ]
then 
    pytest tests

elif [ "x$1" = "x-cov" ]
then
    pytest tests --cov=ansys.scadeone --cov-report html

else
    echo "Bad option $*"
    echo $USAGE
    exit 1
fi