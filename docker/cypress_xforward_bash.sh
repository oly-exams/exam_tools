# for mac see: https://sourabhbajaj.com/blog/2017/02/07/gui-applications-docker-mac/
# docker via Docker Desktop

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
    $SCRIPTPATH/compose.sh run -e DISPLAY=$IP:0 testing_cypress /bin/bash
fi
