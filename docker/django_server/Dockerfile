FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
  git \
  sqlite3 \
  postgresql-client \
  npm \
  nodejs \
  inkscape \
  imagemagick \
  --no-install-recommends && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

RUN npm install -g bower && npm cache clean --force

# create non-root-user
RUN addgroup --gid 5000 container
RUN useradd --create-home --uid 5000 --gid 5000 --shell /bin/bash container
ENV PATH=$PATH:/home/container/.local/bin
USER 5000:5000
WORKDIR /home/container

COPY ./bower.json .
RUN bower install && bower cache clean

# we expect the source to be mounted from extern
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
