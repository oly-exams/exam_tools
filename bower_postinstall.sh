#!/bin/bash

STATIC_BOWER=static_bower
STATIC=static


# ace
cp -r $STATIC_BOWER/ace-builds/src-min $STATIC/
mv $STATIC/src-min $STATIC/ace

# bootstrap and bootstrap-datetimepicker
cp -r $STATIC_BOWER/bootstrap/dist $STATIC/
mv $STATIC/dist $STATIC/bootstrap
cp $STATIC_BOWER/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css $STATIC/bootstrap/css/
cp $STATIC_BOWER/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js $STATIC/bootstrap/js/

# bootstrap-switch
cp -r $STATIC_BOWER/bootstrap-switch/dist $STATIC/
mv $STATIC/dist $STATIC/bootstrap-switch

# ckeditor
cp -r $STATIC_BOWER/ckeditor $STATIC/

# ckeditor_plugins
cp -r $STATIC_BOWER/mathedit/mathedit $STATIC/ckeditor_plugins/
cp -r $STATIC_BOWER/mathjax_4.5.11 $STATIC/ckeditor_plugins/
mv $STATIC/ckeditor_plugins/mathjax_4.5.11 $STATIC/ckeditor_plugins/mathjax-mathquill
cp -r $STATIC_BOWER/VirtualKeyboard.ckeditor.3.7.2.tar $STATIC/ckeditor_plugins/
mv $STATIC/ckeditor_plugins/VirtualKeyboard.ckeditor.3.7.2.tar $STATIC/ckeditor_plugins/Jsvk
# note: bg.js, de-ch.js, eu.js, id.js, ko.js, ug.js were initially not in the repo
patch $STATIC/ckeditor_plugins/mathedit/plugin.js $STATIC/ckeditor_plugins/me_plugin.diff
patch $STATIC/ckeditor_plugins/mathjax-mathquill/plugin.js $STATIC/ckeditor_plugins/mj_plugin.diff
patch $STATIC/ckeditor_plugins/mathjax-mathquill/dev/mathjax.html $STATIC/ckeditor_plugins/mj_dev_mathjax.diff
patch $STATIC/ckeditor_plugins/mathjax-mathquill/dialogs/mathjax.js $STATIC/ckeditor_plugins/mj_dialogs_mathjax.diff
patch $STATIC/ckeditor_plugins/mathjax-mathquill/samples/mathjax.html $STATIC/ckeditor_plugins/mj_samples_mathjax.diff
mv $STATIC/ckeditor_plugins/mathjax-mathquill/dialogs/mathjax.js $STATIC/ckeditor_plugins/mathjax-mathquill/dialogs/mathjax-mathquill.js
mv $STATIC/ckeditor_plugins/mathjax-mathquill/icons/mathjax.png $STATIC/ckeditor_plugins/mathjax-mathquill/icons/mathjax-mathquill.png
mv $STATIC/ckeditor_plugins/mathjax-mathquill/icons/hidpi/mathjax.png $STATIC/ckeditor_plugins/mathjax-mathquill/icons/hidpi/mathjax-mathquill.png

# moment.js
cp $STATIC_BOWER/moment/min/moment.min.js $STATIC/

# MathJax
cp -r $STATIC_BOWER/MathJax $STATIC/

# font-awesome
cp -r $STATIC_BOWER/font-awesome $STATIC/

# jquery
mkdir -p $STATIC/jquery/js
cp $STATIC_BOWER/jquery/dist/jquery.min.js $STATIC/jquery/js/jquery-1.11.2.min.js

# jquery-dirtyfonts
cp -r $STATIC_BOWER/jquery.dirtyforms $STATIC/


# rm -rf $STATIC_BOWER
