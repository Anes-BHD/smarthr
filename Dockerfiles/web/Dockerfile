FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Set working directory
WORKDIR /var/www/smartrh

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
