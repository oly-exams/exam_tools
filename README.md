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
* pandoc (to generate odt exports)

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
pandoc
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
The Cypress tests will automatically run in the CI. If you need to run tests locally, set it up as follows.
1. Use `settings_testing.py`, i.e.
```bash
cp exam_tools/settings_testing.py exam_tools/settings.py
```
2. Adjust any settings, if needed. Make sure not to change the db-settings, however. Cypress will copy the db to (re)initialize, thus the location of the SQLite db needs to be the one set in `settings_testing.py`.

3. Start the dev servers
```bash
./docker/dev_compose.sh up
```

4. Run
```bash
python ipho_data/cypress_initial_data.py
```
inside the django server container to create the initial dataset. This needs to be done before each test, as cypress will override this. Alternatively, you can comment out `cy.exec()` in `e2e/support/commands beforeAllDBInit` and manually create `database-initial` once:
```bash
cp db_data/database.s3db db_data/database-initial.s3db
```
(where `database.s3db` is created by `cypress_initial_data.py`)
5. Start the cypress container with
```bash
./docker/cypress_xforward_bash.sh
```
This will open bash inside the cypress container.
Then you can:
* Run the tests using `cypress run`. If you only want to run one file you can use `cypress run --spec path/to/file`.
* Start the cypress test runner with `cypress open`. This will need X-forwarding to your OS, so you might to install some client (i.e. XMing on Windows).

You can find more about writing tests in the [Cypress readme](e2e/README.md)
