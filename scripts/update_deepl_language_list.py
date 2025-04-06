import os
import sys

# Imports the Deepl client library
import deepl

raw_cred = sys.argv[1]
# Instantiates a client
translate_client = deepl.Translator(raw_cred)
lan_list_source = {l.code for l in translate_client.get_source_languages()}
lan_list_target = {l.code for l in translate_client.get_target_languages()}
with open(
    os.path.join(os.path.dirname(__file__), "../exam_tools/settings.py"), "a"
) as f:
    f.write("DEEPL_SOURCE_LANGUAGES = " + repr(lan_list_source) + "\n")
    f.write("DEEPL_TARGET_LANGUAGES = " + repr(lan_list_target) + "\n")
