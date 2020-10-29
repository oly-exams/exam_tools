FROM cypress/base

# create non-root-user
RUN addgroup --gid 5000 container
RUN useradd --create-home --uid 5000 --gid 5000 --shell /bin/bash container
USER 5000:5000
ENV PATH=$PATH:/home/container/.local/bin
WORKDIR /home/container

RUN ["mkdir", "-p", "cypress/screenshots", "cypress/videos cypress/reports"]

CMD ["/bin/bash", "./cypress_helper.sh"]
