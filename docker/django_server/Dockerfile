FROM python:3.8

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
  git \
  npm \
  patch \
  nodejs \
  sqlite3 \
  inkscape \
  libpq-dev \
  imagemagick \
  postgresql-client \
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

# we need to write as container to these folder
COPY --chown=5000:5000 bower ./bower
RUN cd bower && bower install && bower cache clean && rm -rf static_bower

# we expect the source to be mounted from extern
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
