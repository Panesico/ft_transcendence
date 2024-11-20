FROM  nginx:1.27.1

RUN   mkdir -p /nginx/html/ /etc/nginx/ssl

COPY  ./tools/server-block.conf /etc/nginx/conf.d/

RUN   mkdir -p /var/log/nginx

CMD   ["nginx", "-g", "daemon off;"]
