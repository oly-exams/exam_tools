FROM python:3.8

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
  tidy \
  sqlite3 \
  mercurial \
  libpq-dev \
  postgresql-client \
  inkscape imagemagick \
  texlive texlive-pstricks texlive-xetex texlive-lang-cjk texlive-lang-greek \
  --no-install-recommends && rm -rf /var/lib/apt/lists/*
# fonts-liberation fonts-roboto \
# ttf-mscorefonts-installer fonts-liberation fonts-roboto \

# Alternatively, https://f001.backblazeb2.com/file/olyexams-deploy/texlive-2015.tar.gz
# RUN \
#   curl -o /texlive-2015.tar.gz http://monitor.oly-exams.org:8080/content/texlive-2015.tar.gz \
#   && tar xzf /texlive-2015.tar.gz -C /usr/local/ \
#   && ln -s /usr/local/texlive/2015/bin/x86_64-linux /opt/texbin
COPY ./static/noto/*tf /usr/local/share/fonts/
RUN chmod 644 /usr/local/share/fonts/*tf && dpkg-reconfigure fontconfig-config
RUN apt-get update && apt-get install -y \
    locales \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache -r requirements.txt



# Set the locale
# RUN \
#   echo "LC_ALL=en_US.UTF-8" >> /etc/environment; \
#   echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen; \
#   echo "LANG=en_US.UTF-8" > /etc/locale.conf; \
#   locale-gen en_US.UTF-8

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
  locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ENV CELERY_WORKER=2

RUN mkdir -p /var/run/celery /var/log/celery \
  && chown -R nobody:nogroup /var/run/celery /var/log/celery

CMD /tmp/wait-for-it.sh -t 90 $RABBITMQ_HOST:5672 && celery -A exam_tools worker --statedb=/var/run/celery/worker-example@%h.state -E --concurrency=${CELERY_WORKER} -O fair --uid=nobody --gid=nogroup
