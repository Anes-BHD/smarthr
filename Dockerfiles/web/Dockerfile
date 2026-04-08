FROM nginx:alpine

RUN apk add --no-cache curl

COPY Dockerfiles/web/nginx.conf /etc/nginx/conf.d/default.conf

# public/build/ already exists in context, built by CI runner
COPY public /var/www/smartrh/public

WORKDIR /var/www/smartrh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]