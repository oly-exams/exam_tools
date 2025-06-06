import json
import os
import sys

# Imports the Google Cloud client library
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

raw_cred = sys.argv[1]
str_cred = eval(raw_cred)
# Instantiates a client
json_cred = json.loads(str_cred)
translate_client = translate.Client(
    credentials=service_account.Credentials.from_service_account_info(json_cred)
)
lang_json = translate_client.get_languages()


def append_lang(id, name):
    # check for existing language; if found, do not add it again
    for e in lang_json:
        if e["language"].lower() == id.lower():
            return
    lang_json.append({"language": id, "name": name})


# The Google Translate V2 API is missing some important language variants like en-GB, en-US, pt-BR and pt-PT.
# As we assume that all supported languages (also by DeepL) are supported by Google Translate, we add them manually.
append_lang("en-US", "English (American)")
append_lang("en-GB", "English (British)")
append_lang("pt-BR", "Portugese (Brazil)")
append_lang("pt-PT", "Portugese (Portugal)")

lan_list = json.dumps(lang_json)
with open(
    os.path.join(os.path.dirname(__file__), "../exam_tools/settings.py"), "a"
) as f:
    f.write("AUTO_TRANSLATE_LANGUAGES = " + lan_list + "\n")
