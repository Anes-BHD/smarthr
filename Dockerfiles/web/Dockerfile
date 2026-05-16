FROM nginx:alpine

RUN apk add --no-cache curl

COPY Dockerfiles/web/nginx.conf /etc/nginx/conf.d/default.conf

# ── Static files served directly by Nginx ──────────────────────────────────
# Built by CI runner (npm run build) before this docker build runs.
# laravel-vite-plugin outputs to public/build/
COPY public /var/www/smartrh/public

# Hard fail if manifest is missing — catches silent build failures
RUN test -f /var/www/smartrh/public/build/manifest.json \
    || (echo "❌ ERROR: public/build/manifest.json is missing!" \
        && echo "   Make sure 'npm run build' ran before 'docker build'" \
        && exit 1)

# Create the storage directory that storage:link will point to
# NOTE: In production, mount an EFS volume to /var/www/smartrh/storage/app/public
# so that both backend and web containers share uploaded files.
RUN mkdir -p /var/www/smartrh/storage/app/public \
    && mkdir -p /var/www/smartrh/public/storage \
    && ln -sfn /var/www/smartrh/storage/app/public /var/www/smartrh/public/storage

WORKDIR /var/www/smartrh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]