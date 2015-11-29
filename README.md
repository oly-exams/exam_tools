# IPhO Admin Tools

## Dependencies
Base dependencies
* Python 2.7
* Django 1.7.x
* django-crispy-forms

To compile exams
* XeLaTeX, with TexLive 2014 (2015 not yet tested, but should also work)
* Fonts, TODO provide list of required fonts
* CairoSVG (figure convert)
* pyPDF2 (manipulation of PDF)
* Barcode (generate barcodes)


## Install
1. Create iphoadmin/settings.py, for a simple installation simply copy iphoadmin/settings_example.py
```bash
cp iphoadmin/settings_example.py iphoadmin/settings.py
```

2. Initialize DB
```bash
python manage.py migrate
```

2. Fill with initial data
```bash
TODO... # loaddata xx_name fixtures.
```

3. (optional) Fill with test data
```bash
TODO... # loaddata test_xx_name fixtures.
```

## Running
For the local server, simply execute
```bash
python manage.py runserver
```