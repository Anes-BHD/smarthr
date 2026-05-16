FROM nginx:alpine

RUN apk add --no-cache curl

COPY Dockerfiles/web/nginx.conf /etc/nginx/conf.d/default.conf

# Laravel public assets
COPY public /var/www/smartrh/public

# React SPA built assets — adjust source path to match your actual build output
COPY frontend/dist /var/www/smartrh/frontend

WORKDIR /var/www/smartrh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]