#!/bin/bash

STATIC_BOWER=static_bower
STATIC=static


# ace
cp -r $STATIC_BOWER/ace-builds/src-min/ $STATIC/ace/


# moment.js
cp $STATIC_BOWER/moment/min/moment.min.js $STATIC/



# rm -rf $STATIC_BOWER
