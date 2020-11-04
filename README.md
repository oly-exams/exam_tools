# Exam Tools

## Dependencies
Base dependencies
* Python 3.8
* Django 3.1.x
* django-crispy-forms
* mkdocs (for building the docs)
* bower

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

### Install bower

```bash
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs

sudo npm install -g bower
```


### Development/production environment
The project [ipho2016/deploy](/ipho2016/deploy) provides scripts to deploy a testing environment as well as the final production and demo systems.


## Install
1. Create exam_tools/settings.py, for a simple installation simply copy exam_tools/settings_example.py
```bash
cp exam_tools/settings_example.py exam_tools/settings.py
```

1. If using a virtualenv, make sure it is active

1. Install dependencies using bower, by running at the project root
```bash
cd bower && bower install
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
For the compilation workers, you need to install rabbitmq and then run it by executing
```bash
rabbitmq-server
```
and for the compilation workers
```bash
celery -A exam_tools worker -E --concurrency=1
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

For building docs with custom event target
```bash
python ./scripts/mkdocs_custom.py <name_of_the_event_target>
```

And for locally serving them
```bash
python ./scripts/mkdocs_custom.py -s <name_of_the_event_target>
```
or
```bash
python ./scripts/mkdocs_custom.py -s -a localhost:8080 <name_of_the_event_target>
```

## Docker images
To build the docker images:

```bash
docker build -f docker/Dockerfile.master .
```

## Development with Docker

The development with Docker uses Postgres and RabbitMQ within docker-compose.
The ExamTools code is then executed inside two images containing all required
dependencies. The `docker-compose` environment mounts the local folder inside
the containers, so we can use common IDEs.


1. Use the example settings provided in `./exam_tools/settings_compose.py`

    ```bash
    cp ./exam_tools/settings_compose.py ./exam_tools/settings.py
    ```

2. Launch the docker environment

    ```bash
    docker-compose up
    ```

When needed, one can interact with the Django manage.py using an interactive
session.

```bash
docker-compose run --rm web bash
```

## Using Precommit Hooks
Developers can use the precommit hooks to automatically format the code and get feedback. Install all dev dependencies
```bash
pip install -r requirements_dev.txt
```
followed by:

```bash
pre-commit install
```

Now the precommit hooks will run before every commit, and check the files that where modified. You can also run the hooks manually:

```bash
pre-commit run
pre-commit run --all-files
```


## Testing with Cypress and Django

### Django

Simply run
```bash
python manage.py test
```

### Cypress

1. Install Cypress (https://docs.cypress.io/guides/getting-started/installing-cypress.html)
2. Start the server on localhost:8000 (e.g. with docker-compose)
3. Open the Cypress Test Runner with:
```bash
npx cypress open
```
4. Or run the tests with:
```bash
npx cypress run
```
