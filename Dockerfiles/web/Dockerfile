# Stage 1: Build frontend assets
FROM node:18-alpine AS frontend
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Nginx with compiled assets
FROM nginx:alpine

RUN apk add --no-cache curl

# Nginx config
COPY Dockerfiles/web/nginx.conf /etc/nginx/conf.d/default.conf

# Copy the full public dir including public/build/ from the frontend stage
COPY --from=frontend /app/public /var/www/smartrh/public

WORKDIR /var/www/smartrh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]