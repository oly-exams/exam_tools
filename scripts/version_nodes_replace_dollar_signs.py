import sys
import os
import re

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
sys.path.append(".")

import django

django.setup()

from ipho_exam.models import VersionNode

pattern = r"(?<!\$)\$([^$]+)\$(?!\$)"
repl = r'&lt;span class="math-tex"&gt;\(\1\)&lt;/span&gt;'

if __name__ == "__main__":
    print(
        "This will replace $ by math-tex spans in all version nodes, however, it will only work in the simplest cases, are you sure you want to continue?"
    )
    answer = input("Continue? [y/n/dryrun]")
    if answer.lower() in ["y", "yes", "dryrun"]:
        nodes = VersionNode.objects.all()
        for node in nodes:
            print(
                "========================================================================"
            )
            print(f"VersionNode: {node}")
            if answer.lower() in ["y", "yes"]:
                newtext, count = re.subn(pattern, repl, node.text)
                print(f"Replaced {count} occurances")
                node.text = newtext
                node.save()
            else:
                found = re.findall(pattern, node.text)
                print(f"Found {len(found)} occurances")
                print(
                    "---------------------------------------------------------------------"
                )
                for fi in found:
                    print(fi)
                input("Press any key to continue")
