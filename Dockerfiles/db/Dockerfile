FROM mysql:8.0

# Set default environment variables (can be overridden in docker-compose)
ENV MYSQL_DATABASE=env.DB_DATABASE
ENV MYSQL_USER=env.DB_USERNAME
ENV MYSQL_PASSWORD=env.DB_PASSWORD

# Expose MySQL port
EXPOSE 3306

# Use default MySQL entrypoint
CMD ["mysqld"]
