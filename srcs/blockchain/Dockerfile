FROM node:18

WORKDIR /usr/app

COPY ./tools/package-lock.json ./package-lock.json
COPY ./tools/package.json ./package.json 
COPY ./tools/hardhat.config.js ./hardhat.config.js
COPY ./tools/entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

RUN npm install --save-dev hardhat
EXPOSE 8545

ENTRYPOINT [ "./entrypoint.sh" ]