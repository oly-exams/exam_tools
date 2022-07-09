"""creates a PDF with all passwords for login."""
import subprocess

def fill_main(content):
    tex = f"""
\\documentclass{{article}}

\\usepackage{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage{{graphicx}}

\\pagestyle{{fancy}}

\\fancyhf{{}}
\\fancyhead[OR]{{\\includegraphics[height=5\\baselineskip]{{logo.png}}}}
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
    user name & \\verb\{name}\\ \\\\
    password & \\verb\\{pwd}\\ \\\\
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
    csv = "../../IBO2022/01_initial_data/pws/delegations_credentials.csv"  # path to csv file
    url = "ibo2022.oly-exams.org"  # URL of server
    logo = "logo.png"  # path to logo

    text = ""
    file = "delegation_password_printout.tex"
    skip = True
    with open(csv, "r") as f:
        for line in f.readlines():
            if skip:
                # skip header line
                skip = False
                continue
            array = line.strip("\n").split(",")
            text += set_country(url, *array)

    tex = fill_main(text)


    with open(file, "w") as f:
        f.write(tex)

    subprocess.run(f"pdflatex {file}".split())