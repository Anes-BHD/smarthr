FROM nginx:alpine

RUN apk add --no-cache curl

COPY Dockerfiles/web/nginx.conf /etc/nginx/conf.d/default.conf

# Built by CI runner (npm run build) before this docker build runs.
# laravel-vite-plugin outputs to public/build/ — NOT frontend/dist/
COPY public /var/www/smartrh/public

# Hard fail if manifest is missing — catches silent build failures
RUN test -f /var/www/smartrh/public/build/manifest.json \
    || (echo "❌ ERROR: public/build/manifest.json is missing!" \
        && echo "   Make sure 'npm run build' ran before 'docker build'" \
        && exit 1)

WORKDIR /var/www/smartrh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]