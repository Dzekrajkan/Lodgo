FROM node:20-alpine AS frontend-build

WORKDIR /app
COPY frontend/lodgo .
RUN npm install
RUN npm run build

FROM nginx:alpine

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=frontend-build /app/dist /usr/share/nginx/html