# Exam Tools

## Dependencies

Base dependencies

* Python 3.10+
* Django 4.1.x
* django-crispy-forms
* mkdocs (for building the docs)
* bower

To compile exams

* XeLaTeX
* Fonts, TODO provide list of required fonts
* CairoSVG (figure convert)
* pyPDF2 (manipulation of PDF)
* Barcode (generate barcodes)
* pandoc (to generate odt exports)

### Example Ubuntu packages

On Ubuntu (currently 22.04 LTS), install these packages using ```apt-get```:

```bash
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

For development, also install:

```bash
pip install -r requirements_dev.txt
```

### Install bower

```bash
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs

sudo npm install -g bower
```

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
    ./scripts/loaddata_from.sh <fixtures>
    ```

1. (optional) Fill with test data

    ```bash
    ./scripts/loaddata_from.sh <test_fixtures>
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

(on Macs with Apple Silicon, you need to run ```export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES``` before running celery)

## Building the docs

For development it is suggested to serve the docs locally

```bash
mkdocs serve -a localhost:8001
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

## Development with Docker

To develop with Docker, first install Docker or **update** it to the latest version.

### Quickstart

#### Build and start

To build the Docker images and run them directly via ``docker compose``, run the following command from the root of the project:

```bash
docker compose -f docker/docker-compose-a-dev.yml up --build
```

#### Load test data

The following command loads test data into the server:

```bash
docker exec docker-django-server-1 python ipho_data/main.py
```

Check the file ``ipho_data/test_data/pws/olyexams_superuser_credentials.csv`` for the test superuser credentials.

#### Attach debugger

The django server listens for a debugger on port ``5678``. If you are using VSCode, the following steps can be used to debug the server:

* Open the ``exam_tools`` directory in VSCode [1]
* Copy the ``.vscode/launch.json.example`` file to ``.vscode/launch.json``
* Use the "Debug: Select and Start Debugging" command, and select "Attach to Django server"

[1] When opening the parent directory instead, the ``localRoot`` value in the ``launch.json`` file needs to be adapted to point to the ``exam_tools`` directory.

### Building the Docker images

The following command can be used (from the root of the project) to build the Docker images:

```bash
docker build -f docker/Dockerfile --target<target_name> .
```

The ``<target>`` needs to be replaced with the specific Docker image which should be build.

For "production" images, this can be one of the following:

* ``nginx-with-static``
* ``django-server``
* ``celery-worker``

Alternatively, you can build all "end-use" targets (including testing targets, but not tagging intermediate stages) with

```
docker buildx bake -f docker/bake.hcl
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

1. Adjust any settings, if needed. Make sure not to change the db-settings, however. Cypress will copy the db to (re)initialize, thus the location of the SQLite db needs to be the one set in `settings_testing.py`.

1. Start the dev servers

    ```bash
    ../docker_deploy/docker/dev_compose.sh up
    ```

1. Run

    ```bash
    python ipho_data/cypress_initial_data.py
    ```

    inside the django server container to create the initial dataset. This needs to be done before each test, as cypress will override this. Alternatively, you can comment out `cy.exec()` in `e2e/cypress/support/commands.js` in `beforeAllDBInit` and manually create `database-initial` once:

    ```bash
    cp database.s3db database-initial.s3db
    ```

    (where `database.s3db` is created by `cypress_initial_data.py`)

1. Start the cypress container with

    ```bash
    ../docker_deploy/docker/cypress_xforward_bash.sh
    ```

    This will open bash inside the cypress container.
    Then you can:

    * Run the tests using `cypress run`. If you only want to run one file you can use `cypress run --spec path/to/file`.
    * Start the cypress test runner with `cypress open`. This will need X-forwarding to your OS, so you might to install some client (i.e. XMing on Windows).

    You can find more about writing tests in the [Cypress readme](e2e/README.md)
