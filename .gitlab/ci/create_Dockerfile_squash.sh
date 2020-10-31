# 2020 Oct: the reason why I need this: docker does not support --squash with
# docker-compose build, but I dont want to use docker build, since then we
# are not using any information from the docker-compose.yml build section.
# They reccoment to use multistage builds, but they cannot copy WORKID/USER
# CMD/ENTRYPOINT/ENV.
# This script creates a temporary Dockerfile_squash to squash the images for
# faster/less cluttered CI. Will not be used in production.

echo "FROM scratch" > docker/$1/Dockerfile_squash
echo "COPY --from=$1 / /" >> docker/$1/Dockerfile_squash
grep "ENV\|WORKDIR\|USER\|CMD\|ENTRYPOINT" docker/$1/Dockerfile >> docker/$1/Dockerfile_squash
