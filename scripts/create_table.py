"""create table from csv"""
import argparse
import os
from string import Template
import uuid

import pandas as pd

get_hex = lambda: uuid.uuid4().hex


def csv2xml(file):
    """opens a csv file and creates a xml table. The CSV must not contain
    multirows nor multicols.

    Args:
        file (str): location of the file.

    Returns:
        str: xml as string
    """
    df = pd.read_csv(file, header=None)
    df.fillna("", inplace=True)  # replace None with ""

    col = len(df.columns) * "|l" + "|"
    head = f'<table columns="{col}" top_line="1" id="{get_hex()}">'
    row = Template('<row bottom_line="1" multiplier="1" id="$hex">\n')
    cell = Template('\t<cell id="$hex">$content</cell>\n')

    xml = head
    for _, el in df.iterrows():
        xml += row.substitute(hex=get_hex())
        text = [cell.substitute(hex=get_hex(), content=el[col]) for col in df.columns]
        xml += "".join(text)
        xml += "</row>\n"
    xml += "</table>"
    return xml


def save(xml, name):
    with open(name, "w") as f:
        f.write(xml)


if __name__ == "__main__":
    pathdir = os.path.dirname(os.path.realpath(__file__))
    default_in = os.path.join(pathdir, "ibo2022", "table.csv")
    default_out = os.path.join(pathdir, "ibo2022", "example.xml")

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", type=str, help="input CSV file", default=default_in)
    parser.add_argument("--output", "-o", type=str, help="where to store XML file", default=default_out)

    args = parser.parse_args()
    xml = csv2xml(args.input)
    save(xml, args.output)
    
