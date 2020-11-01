FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
  git \
  --no-install-recommends && apt-get clean && rm -rf /var/lib/apt/lists/*

# create non-root-user
RUN addgroup --gid 5000 container
RUN useradd --create-home --uid 5000 --gid 5000 --shell /bin/bash container
USER 5000:5000
ENV PATH=$PATH:/home/container/.local/bin
WORKDIR /home/container

# we need a dummy git repo
COPY ./requirements.txt ./requirements_dev.txt ./
RUN pip install --no-cache -r requirements.txt -r requirements_dev.txt
RUN git init
COPY .pre-commit-config.yaml .
RUN pre-commit install-hooks
CMD ["pre-commit", "run", "--from-ref", "HEAD~1", "--to-ref", "HEAD"]
