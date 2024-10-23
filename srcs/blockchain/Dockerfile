FROM node:18

ARG   SERVICE_NAME
ENV   SERVICE_NAME=${SERVICE_NAME}

WORKDIR /usr/src/app/${SERVICE_NAME}_app

COPY  ./tools/ /tmp/

RUN chmod +x /tmp/entrypoint.sh

EXPOSE 8545

RUN npm install --save-dev hardhat

ENTRYPOINT [ "/tmp/entrypoint.sh" ]