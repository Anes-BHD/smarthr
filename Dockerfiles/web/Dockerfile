# ── Stage 1: Build the React SPA ─────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /build

# Install deps separately for better layer caching
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
RUN npm run build
# Output → /build/dist/

# ── Stage 2: Nginx web server ─────────────────────────────────────────────────
FROM nginx:alpine

RUN apk add --no-cache curl

COPY Dockerfiles/web/nginx.conf /etc/nginx/conf.d/default.conf

# React SPA built output — served at /
COPY --from=frontend-builder /build/dist /var/www/smartrh/frontend/dist

# Laravel public folder — used only for API PHP routing and static assets
COPY public /var/www/smartrh/public

# Create storage directory and symlink for Laravel uploaded files
RUN mkdir -p /var/www/smartrh/storage/app/public \
    && ln -sfn /var/www/smartrh/storage/app/public /var/www/smartrh/public/storage

# Hard fail if React SPA index.html is missing
RUN test -f /var/www/smartrh/frontend/dist/index.html \
    || (echo "❌ ERROR: frontend/dist/index.html is missing!" && exit 1)

WORKDIR /var/www/smartrh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]