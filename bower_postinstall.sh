#!/bin/bash

STATIC_BOWER=static_bower
STATIC=static


# ace
cp -r $STATIC_BOWER/ace-builds/src-min/ $STATIC/ace/

# bootstrap and bootstrap-datetimepicker
cp -r $STATIC_BOWER/bootstrap/dist/ $STATIC/bootstrap/
cp $STATIC_BOWER/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css $STATIC/bootstrap/css/
cp $STATIC_BOWER/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js $STATIC/bootstrap/js/

# bootstrap-switch
cp -r $STATIC_BOWER/bootstrap-switch/dist/ $STATIC/bootstrap-switch/

# ckeditor
cp -r $STATIC_BOWER/ckeditor/ $STATIC/ckeditor/

# moment.js
cp $STATIC_BOWER/moment/min/moment.min.js $STATIC/

# MathJax
cp -r $STATIC_BOWER/MathJax $STATIC/

# rm -rf $STATIC_BOWER
