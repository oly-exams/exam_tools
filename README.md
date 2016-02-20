# IPhO Admin Tools

## Dependencies
Base dependencies
* Python 2.7
* Django 1.8.x
* django-crispy-forms

To compile exams
* XeLaTeX, with TexLive 2014 (2015 not yet tested, but should also work)
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
python-cairosvg
```

Then using ```pip```:
```bash
pip install -r requirements.txt
```


### Development/production environment
The project [ipho2016/deploy](/ipho2016/deploy) provides scripts to deploy a testing environment as well as the final production and demo systems.


## Install
1. Create iphoadmin/settings.py, for a simple installation simply copy iphoadmin/settings_example.py
```bash
cp iphoadmin/settings_example.py iphoadmin/settings.py
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