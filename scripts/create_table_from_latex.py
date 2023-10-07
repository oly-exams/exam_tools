"""create table from latex"""
import argparse
import html
import os
import re
import uuid

get_hex = lambda: uuid.uuid4().hex


def ensure_escaped(s):
    if (
        re.search(r"[\\~]|\d\.\d", s) is not None
        and re.search(r"\$|\\[\[(]", s) is None
    ):
        s = "$" + s + "$"
    return html.escape(s)


def make_multi_escape(s):
    begin = "\\multicolumn"
    if s.startswith(begin):
        assert s[len(begin)] == "{"
        assert s.endswith("}")
        parts = []
        last_i = None
        lvl = 0
        for i, c in enumerate(s):
            if i < len(begin):
                continue
            if c == "{":
                if lvl == 0:
                    last_i = i
                lvl += 1
            if c == "}":
                lvl -= 1
                if lvl == 0:
                    parts.append(s[last_i + 1 : i])
                    last_i = None
        assert lvl == 0, s
        assert len(parts) == 3
        return (
            f"""<multicolumncell columns="{parts[1]}" size="{parts[0]}" id="{get_hex()}">{ensure_escaped(parts[2])}</multicolumncell>""",
            int(parts[0]),
        )
    else:
        return ensure_escaped(s), 1


def tex2xml(file):
    """opens a tex file and creates a xml table. The TeX must not contain
    multirows; multicols are supported. Use at your own risk, fancy features
    may not work as expected.

    Args:
        file (str): location of the file.

    Returns:
        str: xml as string
    """
    with open(file) as f:
        content = f.read()
    begin = "\\begin{tabular}"
    end = "\\end{tabular}"
    i = content.find(begin)
    colspec = None
    if i != -1:
        content = content[i + len(begin) :].strip()
        assert content.startswith("{")
        k = 1
        i = 1
        while True:
            if i >= len(content):
                assert False, content
            if content[i] == "{":
                k += 1
            elif content[i] == "}":
                k -= 1
            if k == 0:
                colspec = content[1:i]
                content = content[i + 1 :]
                break
            i += 1
    j = content.find(end)
    if j != -1:
        content = content[:j].strip()
    assert "\\multirow" not in content
    hline = "\\hline"
    lines_before = 0
    rows = [r.strip() for r in content.split("\\\\")]
    lines_after = [0 for __ in rows]
    for i, row in enumerate(rows):
        while row.startswith(hline):
            row = row[len(hline) :].strip()
            if i == 0:
                lines_before += 1
            else:
                lines_after[i - 1] += 1
        rows[i] = row
    if not rows[-1]:
        assert lines_after[-1] == 0
        rows = rows[:-1]
        lines_after = lines_after[:-1]
    cells = [
        [make_multi_escape(c.strip()) for c in re.split(r"(?<!\\)&", row)]
        for row in rows
    ]
    sizes = [[c[1] for c in row] for row in cells]
    cells = [[c[0] for c in row] for row in cells]
    n = max(sum(size) for size in sizes)
    #    for i, (row, size) in enumerate(zip(cells, sizes)):
    #        if sum(size) < n:
    #            cells[i] = row + [""]*(n - sum(size))
    if colspec is None:
        colspec = "|l" * n + "|"

    xml = f'<table columns="{colspec}" top_line="{lines_before}" id="{get_hex()}">\n'
    for row, bline in zip(cells, lines_after):
        xml += f'<row bottom_line="{bline}" multiplier="1" id="{get_hex()}">\n'
        text = [f'\t<cell id="{get_hex()}">{cell}</cell>\n' for cell in row]
        xml += "".join(text)
        xml += "</row>\n"
    xml += "</table>"
    return xml


def save(xml, name):
    with open(name, "w") as f:
        f.write(xml)


if __name__ == "__main__":
    pathdir = os.path.dirname(os.path.realpath(__file__))
    default_in = os.path.join(pathdir, "input_examples", "table.tex")
    default_out = os.path.join(pathdir, "input_examples", "example.xml")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", "-i", type=str, help="input LaTeX file", default=default_in
    )
    parser.add_argument(
        "--output", "-o", type=str, help="where to store XML file", default=default_out
    )

    args = parser.parse_args()
    xml = tex2xml(args.input)
    save(xml, args.output)
