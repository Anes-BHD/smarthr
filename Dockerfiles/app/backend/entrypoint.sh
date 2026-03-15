#!/bin/bash
set -e

# Only run composer install if vendor is missing
if [ ! -f /var/www/smartrh/vendor/autoload.php ]; then
    composer install --working-dir=/var/www/smartrh --no-interaction
fi

chmod -R 777 /var/www/smartrh/storage /var/www/smartrh/bootstrap/cache
chown -R www-data:www-data /var/www/smartrh/storage /var/www/smartrh/bootstrap/cache

# Wait for MySQL to be ready using TCP check
echo "Waiting for database..."
until (echo > /dev/tcp/db/3306) 2>/dev/null; do
    echo "DB not ready, retrying in 3s..."
    sleep 3
done
echo "Database is ready!"

php /var/www/smartrh/artisan migrate --force --no-interaction 2>&1 || true

USER_COUNT=$(php /var/www/smartrh/artisan tinker --execute="echo \App\Models\User::count();" 2>/dev/null | tail -1)
if [ "$USER_COUNT" = "0" ]; then
    php /var/www/smartrh/artisan db:seed --force
fi

exec php-fpm
