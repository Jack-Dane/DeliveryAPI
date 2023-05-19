FROM node:20

COPY homeDelivery/package.json /
COPY homeDelivery/package-lock.json /

RUN npm install

COPY . /web
WORKDIR /web/homeDelivery

CMD npm run dev