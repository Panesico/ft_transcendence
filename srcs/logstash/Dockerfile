ARG ELKF_VERSION
FROM docker.elastic.co/logstash/logstash:${ELKF_VERSION}

RUN chmod -R 777 /usr/share/logstash
RUN chown -R logstash:logstash /usr/share/logstash