"""creates a PDF with all passwords for login."""
import subprocess
import os

def fill_main(content, logo):
    tex = f"""
\\documentclass{{article}}

\\usepackage{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage{{graphicx}}

\\pagestyle{{fancy}}

\\fancyhf{{}}
\\fancyhead[OR]{{\\includegraphics[height=5\\baselineskip]{{ {logo} }}}}
\\addtolength{{\\headheight}}{{5\\baselineskip}}

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
    URL & \href{{{url}}}{{{url}}} \\\\
    Country &  {full_name} \\\\
    user name & \\verb\\{name}\\ \\\\
    password & \\verb\\{pwd}\\ \\\\
    \\\\
    WiFi SSID & \\verb\\IBO2022_5\\ \\\\
    WiFi password & \\verb@IBO2022@ \\\\
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
    csv = os.path.join(pathdir, "ibo2022", "delegations_credentials.csv")  # path to csv file
    url = "ibo2022.oly-exams.org"  # URL of server
    logo = os.path.join(pathdir, "ibo2022", "logo.png")  # path to logo

    text = ""
    file = os.path.join(pathdir, "ibo2022", "delegation_password_printout.tex")
    skip = True
    with open(csv, "r") as f:
        for line in f.readlines():
            if skip:
                # skip header line
                skip = False
                continue
            array = line.strip("\n").split(",")
            text += set_country(url, *array)

    tex = fill_main(text, logo)


    with open(file, "w") as f:
        f.write(tex)

    subprocess.run(f"pdflatex -output-directory=ibo2022 {file}".split())