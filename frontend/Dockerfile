FROM node:20-alpine as build

WORKDIR /frontend

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM node:20-alpine

WORKDIR /frontend

RUN npm install -g serve

COPY --from=build /frontend/dist ./dist

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]
