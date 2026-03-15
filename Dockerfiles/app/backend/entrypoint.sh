#!/bin/bash
set -e

# Only run composer install if vendor is missing
if [ ! -f /var/www/smartrh/vendor/autoload.php ]; then
    composer install --working-dir=/var/www/smartrh --no-interaction
fi

chmod -R 777 /var/www/smartrh/storage /var/www/smartrh/bootstrap/cache
chown -R www-data:www-data /var/www/smartrh/storage /var/www/smartrh/bootstrap/cache

# Wait for MySQL to be ready
echo "Waiting for database..."
until php /var/www/smartrh/artisan db:monitor --databases=mysql 2>/dev/null; do
    sleep 2
done

# Use migrate --skip-existing or just ignore errors from already-existing tables
php /var/www/smartrh/artisan migrate --force --no-interaction 2>&1 || true

# Only seed if no users exist
USER_COUNT=$(php /var/www/smartrh/artisan tinker --execute="echo \App\Models\User::count();" 2>/dev/null | tail -1)
if [ "$USER_COUNT" = "0" ]; then
    php /var/www/smartrh/artisan db:seed --force
fi

exec php-fpm
