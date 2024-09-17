FROM  python:3.9.20-alpine3.20

RUN   apk update && \
  apk add postgresql-client && \
  rm -rf /var/cache/apk/*

WORKDIR /usr/src/app

COPY  ./tools/init_django.sh .
COPY  ./tools/requirements.txt .

RUN chmod +x init_django.sh

# Install Python dependencies - Django version specified in requirements.txt
# RUN   pip install -r requirements.txt
RUN   pip install Django==4.2.16

EXPOSE 9000

ENTRYPOINT [ "/bin/sh", "init_django.sh" ]

CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]
