FROM  python:3.9.20-alpine3.20

RUN   apk update && \
  apk add postgresql-client nodejs npm git expect && \
  rm -rf /var/cache/apk/*

RUN   pip install --upgrade pip

ARG   SERVICE_NAME
ENV   SERVICE_NAME=${SERVICE_NAME}
WORKDIR /usr/src/app/${SERVICE_NAME}_app

COPY  ./tools/ /tmp/


# Install Python dependencies specified in requirements.txt
RUN   pip install -r /tmp/requirements.txt

RUN   chmod +x /tmp/init_django.sh
RUN  chmod +x /tmp/init_hardat.sh

# hardat config js file
COPY ./tools/hardat_config.js /tmp/hardat_config.js

#ENTRYPOINT [ "/bin/sh", "/tmp/init_django.sh" ]
ENTRYPOINT [ "/bin/sh", "/tmp/init_hardat.sh" ]

