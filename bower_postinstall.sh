#!/bin/bash

STATIC_BOWER=static_bower
STATIC=static

# moment.js
cp $STATIC_BOWER/moment/min/moment.min.js $STATIC/

# MathJax
cp -r $STATIC_BOWER/MathJax $STATIC/

# rm -rf $STATIC_BOWER