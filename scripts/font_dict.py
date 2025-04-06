import os
import re
import sys

family_pattern = re.compile(r"font-family:[ ]+\'([^\']+)\'")
family_pattern = re.compile(r"font-family:[ ]+\'([^\']+)\'")

cjk_list = ["notosansjp", "notosanskr", "notosanssc", "notosanstc"]

results = []

flist = sys.argv[1:]
for css_file in flist:
    for line in open(css_file):
        match = family_pattern.search(line)
        if match:
            css_name = os.path.basename(css_file)
            name = css_name.replace(".css", "")
            results.append(
                {
                    "css": css_name,
                    "name": name.replace(".css", ""),
                    "font": match.group(1),
                    "cjk": int(name in cjk_list),
                }
            )
results = {v["name"]: v for v in results}
import json

print("noto =", json.dumps(results, indent=2))
