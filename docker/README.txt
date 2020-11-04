We can use "create_squash_file.py SERVICE_NAME" to create or update the
Dockerfile_squash in the corresponding folder. The main reason we want to
do this, is because the gitlab CI becomes less cluttered/faster. Docker
itself has an experimental feature --squash, but only for "docker build",
not for "docker-compose build" which we want to use.

During build:
The CI pipeline checks if there is Dockerfile_squash file available. If not
it will use the normal image, nobody is forced to use the squash optimization.
