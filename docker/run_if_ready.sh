#!/bin/sh
set -e

COMMAND=$1
WAIT_FOR=$2

SCRIPT=$(readlink -f $0)
SCRIPTPATH=$(dirname $SCRIPT)

for HOST_PORT in $WAIT_FOR
do
    $SCRIPTPATH/wait-for-it.sh $HOST_PORT --timeout=60
done

eval $COMMAND
