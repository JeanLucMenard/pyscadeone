# This script sources the activate script from
# a python virtual environment. The script path depends
# on the OS.
# 
# Usage: source activate.sh <env path>
#     
VENV=${1?"Missing venv argument"}

case $OSTYPE in
    linux*)
        ACTIVATE_SCRIPT=$VENV/bin/activate
        ;;

    msys*)
        ACTIVATE_SCRIPT=$VENV/Scripts/activate
        ;;

    cygwin*)
        ACTIVATE_SCRIPT=$VENV/Scripts/activate
        dos2unix $ACTIVATE_SCRIPT
        ;;

    *)
        echo "*** Unknown: $OSTYPE"
        exit 1
        ;; 
esac

if [ -f "$ACTIVATE_SCRIPT" ]
then
    source "$ACTIVATE_SCRIPT"
else
    echo "*** No activation script: $ACTIVATE_SCRIPT"
    exit 1
fi
