FROM nginx:alpine

RUN apk add --no-cache curl

# nginx config
COPY Dockerfiles/web/nginx.conf /etc/nginx/conf.d/default.conf

# copy built static assets
COPY public /var/www/smartrh/public

WORKDIR /var/www/smartrh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]