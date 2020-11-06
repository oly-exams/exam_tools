#!/bin/sh

SCRIPT=$(readlink -f $0)
SCRIPTPATH=$(dirname $SCRIPT)

UNAME=$(uname -s)


if [ $UNAME = "Linux"  ]
then
    $SCRIPTPATH/compose.sh -f "$SCRIPTPATH/overwrite/cypress_xforward_win.yml" run testing_cypress /bin/bash
elif [ $UNAME = "Darwin" ]
then
    IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
    echo "make sure xQuarz is running and xhost is known in PATH"
    xhost + $IP
    DISPLAY=$IP:0 $SCRIPTPATH/compose.sh -f "$SCRIPTPATH/overwrite/cypress_xforward_osx.yml" run testing_cypress /bin/bash
fi
