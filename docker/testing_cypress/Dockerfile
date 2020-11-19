# 2020, Oct: cypress does not offer a latest tag
FROM cypress/included:5.5.0

# install comparepdf
RUN apt-get update && apt-get install -y \
  comparepdf \
  --no-install-recommends && apt-get clean && rm -rf /var/lib/apt/lists/*
# create non-root-user
RUN addgroup --gid 5000 container
RUN useradd --create-home --uid 5000 --gid 5000 --shell /bin/bash container
USER 5000:5000
ENV PATH=$PATH:/home/container/.local/bin
WORKDIR /home/container

RUN ["mkdir", "-p", "cypress/screenshots", "cypress/videos", "cypress/reports", "cypress/pdfs"]
# its not considered good practice to set entrypoint if a CMD can do the same
# clearing the parent images entrypoint
ENTRYPOINT []
CMD npx wait-on http-get://localhost:8000 && cypress run --headless -b chrome
