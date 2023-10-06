"""generate_answer_sheet.py

This is useful for computer-base exams, which do not require
translation of an answer sheet. For the marking, we still
need an answer sheet. This will create a minimalistic
answer sheet, which can be uploaded in Exam management.
After that, you can import the marking scheme as usual.
(In the future, we should allow uploading the marks
without specifying an answer sheet).
"""
import argparse
import secrets
from string import Template

import pandas as pd

template = Template(
    '<subanswer points="$points" part_nr="$part_nr" question_nr="$question_nr" id="$id" />'
)


def generate_answer_box(question_nr, points, part_nr="Q"):
    id = secrets.token_hex(32)
    try:
        if abs(int(question_nr) - question_nr) < 1e-10:
            question_nr = int(question_nr)
    except:
        pass
    return template.substitute(
        points=points, part_nr=part_nr, question_nr=question_nr, id=id
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--points-file",
        required=True,
        help="CSV file with two columns: Question number and Points",
    )
    parser.add_argument(
        "--output-xml",
        default="answer_sheet.xml",
        help="Output file, where xml output is written to",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.points_file)
    output = f'<question points="{df["Points"].sum()}" id="q0"><title id="title0">Question title</title>\n'
    for i in range(len(df)):
        output += generate_answer_box(df["Question"][i], df["Points"][i]) + "\n"
    output += "</question>\n"

    with open(args.output_xml, "w") as f:
        f.write(output)

    print(f"Output written to {args.output_xml}")
