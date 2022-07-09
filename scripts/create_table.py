"""create table from csv"""
import pandas as pd
import uuid
from string import Template

get_hex = lambda: uuid.uuid4().hex


def csv2xml(file):
    """opens a csv file and creates a xml table. The CSV must not contain
    multirows nor multicols.

    Args:
        file (str): location of the file.

    Returns:
        str: xml as string
    """
    df = pd.read_csv(file)

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
    input = "020_delegations.csv"
    output = "example.xml"
    xml = csv2xml(input)
    save(xml, output)
    
    