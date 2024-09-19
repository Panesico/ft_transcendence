FROM  python:3.9.20-alpine3.20

RUN   apk update && \
  apk add postgresql-client && \
  rm -rf /var/cache/apk/*

WORKDIR /usr/src/app

COPY  ./tools/init_django.sh /tmp/init_django.sh
COPY  ./tools/requirements.txt /tmp/requirements.txt

RUN   chmod +x /tmp/init_django.sh

# Install Python dependencies specified in requirements.txt
RUN   pip install --upgrade pip
RUN   pip install -r /tmp/requirements.txt

EXPOSE 9000

ENTRYPOINT [ "/bin/sh", "/tmp/init_django.sh" ]

CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]
