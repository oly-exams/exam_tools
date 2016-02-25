#!/bin/sh

## Download .css files
curl https://www.google.com/fonts/earlyaccess | grep import\ url | grep noto | sed 's/@import url(//g' | sed 's/);//g' | sed 's/<b>//g' | sed 's/<\/b>//g' | xargs -n1 curl -O

## Download Noto Sans and Serif
## from: http://www.localfont.com


## Download all font files in the css
cat *.css | grep url | sed 's/url(/http:/g' | sed -e 's/).*//g' | xargs -n1 curl -OL

## Rename iefix
for ll in `ls *iefix`; do mv "$ll" "$(echo $ll | sed 's/?#iefix//g')"; done

## Rename filename in .css
sed -i "" 's,//fonts.gstatic.com/ea/notosansvai/v1/,/static/noto/,g' *.css
