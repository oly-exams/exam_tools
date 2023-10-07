"""creates a PDF with all passwords for login."""
import argparse
import os
import subprocess


def fill_main(content, oe_logo, logo):
    tex = f"""
\\documentclass[a5paper, landscape]{{article}}
\\usepackage[margin=3cm]{{geometry}}
\\usepackage[T1]{{fontenc}}
\\usepackage[ttdefault=true]{{AnonymousPro}}
%\\renewcommand*\\familydefault{{\\ttdefault}}

\\usepackage{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage{{graphicx}}

\\pagestyle{{fancy}}

\\fancyhf{{}}
\\fancyhead[OL]{{\\includegraphics[height=5\\baselineskip]{{ {oe_logo} }}}}
\\fancyhead[OR]{{\\includegraphics[height=5\\baselineskip]{{ {logo} }}}}
\\addtolength{{\\headheight}}{{5\\baselineskip}}
\\setlength\\parindent{{0pt}}

\\begin{{document}}

\\begin{{huge}}

    {content}

\\end{{huge}}

\\end{{document}}
"""
    return tex


def set_country(url, full_name, name, pwd):
    tex = f"""
\\begin{{tabular}}{{ll}}
    URL & \\texttt{{\\href{{https://{url}}}{{{url}}}}} \\\\
    Country &  {full_name} \\\\
    User name & \\verb\\{name}\\ \\\\
    Password & \\verb\\{pwd}\\ \\\\
    \\\\
    WI-FI SSID & \\texttt{{Planeta}} \\\\
    WI-FI password & \\texttt{{Planeta2023}} \\\\
\\end{{tabular}}
\\clearpage
\\newpage

    """
    return tex


if __name__ == "__main__":
    # We expect the csv file to be in the following format:
    # Country Name,Country Code,pws
    # Argentina,ARG,pwd1
    # Armenia,ARM,pwd2
    pathdir = os.path.dirname(os.path.realpath(__file__))
    csv = os.path.join(pathdir, "delegations_credentials.csv")  # path to csv file
    file = os.path.join(pathdir, "input_examples", "delegation_password_printout.tex")

    url = "ioaa2023.oly-exams.org"  # URL of server
    oe_logo = os.path.join(
        pathdir, "../static", "logo_square.png"
    )  # path to OlyExams logo
    logo = os.path.join(pathdir, "../static", "ioaa2023_logo.png")  # path to logo

    text = ""
    skip = True
    with open(csv) as f:
        for line in f.readlines():
            if skip:
                # skip header line
                skip = False
                continue
            array = line.strip("\n").split(",")
            text += set_country(url, *array)

    tex = fill_main(text, oe_logo, logo)

    with open(file, "w") as f:
        f.write(tex)

    subprocess.run(f"pdflatex -output-directory=input_examples {file}".split())
