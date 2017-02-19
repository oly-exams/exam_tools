#!/bin/bash

STATIC_BOWER=static_bower
STATIC=static
BOWER_POSTINSTALL=bower_postinstall


# ace
cp -r $STATIC_BOWER/ace-builds/src-min $STATIC/ace

# bootstrap and bootstrap-datetimepicker
cp -r $STATIC_BOWER/bootstrap/dist $STATIC/
mv $STATIC/dist $STATIC/bootstrap
cp $STATIC_BOWER/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css $STATIC/bootstrap/css/
cp $STATIC_BOWER/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js $STATIC/bootstrap/js/

# bootstrap-switch
cp -r $STATIC_BOWER/bootstrap-switch/dist $STATIC/bootstrap-switch

# TODO
# ckeditor
#patch $STATIC_BOWER/ckeditor/ckeditor.js $BOWER_POSTINSTALL/ck_editor.diff
#patch $STATIC_BOWER/ckeditor/lang/en.js $BOWER_POSTINSTALL/ck_langen.diff
#cp -r $STATIC_BOWER/ckeditor $STATIC/

# ckeditor_plugins
mkdir $STATIC/ckeditor_plugins
patch $STATIC_BOWER/mathedit/mathedit/plugin.js $BOWER_POSTINSTALL/me_plugin.diff
patch $STATIC_BOWER/mathjax_4.5.11/plugin.js $BOWER_POSTINSTALL/mj_plugin.diff
patch $STATIC_BOWER/mathjax_4.5.11/dev/mathjax.html $BOWER_POSTINSTALL/mj_dev_mathjax.diff
patch $STATIC_BOWER/mathjax_4.5.11/dialogs/mathjax.js $BOWER_POSTINSTALL/mj_dialogs_mathjax.diff
patch $STATIC_BOWER/mathjax_4.5.11/samples/mathjax.html $BOWER_POSTINSTALL/mj_samples_mathjax.diff
cp -r $STATIC_BOWER/mathedit/mathedit $STATIC/ckeditor_plugins/
cp -r $STATIC_BOWER/mathjax_4.5.11 $STATIC/ckeditor_plugins/mathjax-mathquill
cp -r $STATIC_BOWER/VirtualKeyboard.ckeditor.3.7.2.tar $STATIC/ckeditor_plugins/Jsvk
# note: bg.js, de-ch.js, eu.js, id.js, ko.js, ug.js were initially not in the repo
mv $STATIC/ckeditor_plugins/mathjax-mathquill/dialogs/mathjax.js $STATIC/ckeditor_plugins/mathjax-mathquill/dialogs/mathjax-mathquill.js
mv $STATIC/ckeditor_plugins/mathjax-mathquill/icons/mathjax.png $STATIC/ckeditor_plugins/mathjax-mathquill/icons/mathjax-mathquill.png
mv $STATIC/ckeditor_plugins/mathjax-mathquill/icons/hidpi/mathjax.png $STATIC/ckeditor_plugins/mathjax-mathquill/icons/hidpi/mathjax-mathquill.png

# moment.js
cp $STATIC_BOWER/moment/min/moment.min.js $STATIC/

# clipboard.js
cp $STATIC_BOWER/clipboard/dist/clipboard.min.js $STATIC/

# MathJax
cp -r $STATIC_BOWER/MathJax $STATIC/

# font-awesome
cp -r $STATIC_BOWER/font-awesome $STATIC/

# jquery
mkdir -p $STATIC/jquery/js
cp $STATIC_BOWER/jquery/dist/jquery.min.js $STATIC/jquery/js/jquery-1.11.2.min.js

# jquery-dirtyforms
cp -r $STATIC_BOWER/jquery.dirtyforms $STATIC/jquery-dirtyforms

# django ace
cp -r python -c `"import django_ace;import os;print os.path.join(os.path.dirname(django_ace.__file__), 'static')"` $STATIC/


# rm -rf $STATIC_BOWER
