#!/bin/bash
chmod -R 777 /var/www/smartrh/storage /var/www/smartrh/bootstrap/cache
chown -R www-data:www-data /var/www/smartrh/storage /var/www/smartrh/bootstrap/cache

composer install --working-dir=/var/www/smartrh

php /var/www/smartrh/artisan migrate --force

# Only seed if no users exist
USER_COUNT=$(php /var/www/smartrh/artisan tinker --execute="echo \App\Models\User::count();" 2>/dev/null | tail -1)
if [ "$USER_COUNT" = "0" ]; then
    php /var/www/smartrh/artisan db:seed --force
fi

exec php-fpm
