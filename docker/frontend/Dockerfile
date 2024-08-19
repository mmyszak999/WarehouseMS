FROM node:14-alpine

WORKDIR /frontend-code

COPY ./frontend/package.json .

RUN npm install

COPY ./frontend .

CMD ["npm", "start"]