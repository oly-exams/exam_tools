# IPhO Admin Tools

## Dependencies
Base dependencies
* Python 2.7
* Django 1.8.x
* django-crispy-forms
* mkdocs (for building the docs)

To compile exams
* XeLaTeX, with TexLive 2015 (2013 does not work with Noto Fonts and CJK). See [texlive/install.md](texlive/install.md) for installation details.
* Fonts, TODO provide list of required fonts
* CairoSVG (figure convert)
* pyPDF2 (manipulation of PDF)
* Barcode (generate barcodes)

### Example Ubuntu packages
On Ubuntu 14.04, install these packages using ```apt-get```:
```
git
python-dev
python-psycopg2 # only if using PostgreSQL DB
python-virtualenv
python-pip
mercurial
libffi-dev
libzbar-dev
python-cairosvg
texlive
texlive-xetex
texlive-lang-cjk
texlive-lang-greek
fonts-roboto
ttf-mscorefonts-installer # this requires the multiverse packages in Ubuntu!!
fonts-liberation
```

Then using ```pip```:
```bash
pip install -r requirements.txt
```


### Development/production environment
The project [ipho2016/deploy](/ipho2016/deploy) provides scripts to deploy a testing environment as well as the final production and demo systems.


## Install
1. Create exam_tools/settings.py, for a simple installation simply copy exam_tools/settings_example.py
```bash
cp exam_tools/settings_example.py exam_tools/settings.py
```

1. Initialize DB
```bash
python manage.py migrate
```

1. Fill with initial data
```bash
TODO... # loaddata xx_name fixtures.
```

1. (optional) Fill with test data
```bash
TODO... # loaddata test_xx_name fixtures.
```

## Running
For the local server, simply execute
```bash
python manage.py runserver
```

## Running the workers **locally**
Add to exam_tools/settings.py:
```
BROKER_URL = 'django://'
INSTALLED_APPS = INSTALLED_APPS + ('kombu.transport.django',)
```

Execute: 
```
python manage.py migrate kombu_transport_django
```

Start workers with
```
celery -A exam_tools worker -E --concurrency=2
```

## Building the docs
For development it is suggested to serve the docs locally
```bash
mkdocs serve
```

For building the static docs
```bash
mkdocs build
```
