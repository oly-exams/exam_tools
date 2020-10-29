ARG SERVER_IMG=django_server

FROM $SERVER_IMG

#server image runs non-root user, get back root
USER root:root

RUN apt-get update && apt-get install -y \
  libgtk2.0-0 \
  libgtk-3-0 \
  libgbm-dev \
  libnotify-dev \
  libgconf-2-4 \
  libnss3 \
  libxss1 \
  libasound2 \
  libxtst6 \
  xauth \
  xvfb \
  --no-install-recommends && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN npm -g install cypress --unsafe-perm=true --save-dev cypress \
    && npm cache clean  --force

# return to non-root user
USER 5000:5000

RUN cypress install --force

RUN ["mkdir", "-p", "cypress/screenshots", "cypress/videos cypress/reports"]
USER root:root

CMD /bin/bash ./cypress_helper.sh
