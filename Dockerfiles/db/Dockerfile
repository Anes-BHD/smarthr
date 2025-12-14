FROM mysql:8.0

# Set default environment variables (can be overridden in docker-compose)
ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_DATABASE=smartrh
ENV MYSQL_USER=smartrh
ENV MYSQL_PASSWORD=password

# Expose MySQL port
EXPOSE 3306

# Use default MySQL entrypoint
CMD ["mysqld"]
