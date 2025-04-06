import os
import re
import sys

from cssutils import css, stylesheets

family_pattern = re.compile(r"url\(([^)]+)\) +format\(([^)]+)\)")

cjk_list = ["notosansjp", "notosanskr", "notosanssc", "notosanstc"]

results = []

flist = sys.argv[1:]
for css_file in flist:
    css_name = os.path.basename(css_file)
    name = css_name.replace(".css", "")
    cssdict = {
        "css": css_name,
        "name": name,
        # 'font': None,
        "cjk": int(name in cjk_list),
    }

    sheet = css.CSSStyleSheet()
    sheet.cssText = open(css_file).read()
    for rule in sheet:
        if rule.type == rule.FONT_FACE_RULE:
            matches = family_pattern.findall(rule.style.src)
            for url, fmt in matches:
                if fmt.strip('"') in ["truetype", "opentype"]:
                    font_file = os.path.basename(url)
                    if (
                        rule.style.fontWeight == "400"
                        and rule.style.fontStyle == "normal"
                    ):
                        cssdict["font"] = rule.style.fontFamily.strip("\"'")
                        cssdict["font_regular"] = font_file
                    elif (
                        rule.style.fontWeight == "400"
                        and rule.style.fontStyle == "italic"
                    ):
                        cssdict["font_italic"] = font_file
                    elif (
                        rule.style.fontWeight == "700"
                        and rule.style.fontStyle == "normal"
                    ):
                        cssdict["font_bold"] = font_file
                    elif (
                        rule.style.fontWeight == "700"
                        and rule.style.fontStyle == "italic"
                    ):
                        cssdict["font_bolditalic"] = font_file

    if "font_regular" in cssdict:
        results.append(cssdict)
    else:
        sys.stderr.write(f"Error with {css_name}. Font regular not found.\n")

results = {v["name"]: v for v in results}
import json

print("noto =", json.dumps(results, indent=2))
