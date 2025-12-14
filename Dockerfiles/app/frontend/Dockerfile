FROM node:20-alpine

# Set working directory
WORKDIR /var/www/smartrh

# Install dependencies
RUN apk add --no-cache git

# Copy package files
COPY package*.json ./

# Install npm dependencies
RUN npm ci

# Expose Vite dev server port (if running in dev mode)
EXPOSE 5173
