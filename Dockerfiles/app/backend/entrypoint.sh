#!/bin/bash
set -e

echo "Setting permissions..."
chmod -R 775 /var/www/smartrh/storage /var/www/smartrh/bootstrap/cache
chown -R www-data:www-data /var/www/smartrh/storage /var/www/smartrh/bootstrap/cache

cat > /var/www/smartrh/.env <<EOF
APP_NAME=${APP_NAME:-Smarthr}
APP_ENV=${APP_ENV:-production}
APP_KEY=${APP_KEY}
APP_DEBUG=${APP_DEBUG:-false}
APP_URL=${APP_URL:-https://smarthr.anesbhd.com}

LOG_CHANNEL=stderr
LOG_LEVEL=debug
TRUSTED_PROXIES=*
SESSION_SECURE_COOKIE=true

DB_CONNECTION=mysql
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT:-3306}
DB_DATABASE=${DB_DATABASE}
DB_USERNAME=${DB_USERNAME}
DB_PASSWORD=${DB_PASSWORD}

SESSION_DRIVER=database
SESSION_LIFETIME=120

CACHE_STORE=redis
REDIS_CLIENT=${REDIS_CLIENT:-phpredis}
REDIS_HOST=${REDIS_HOST:-smarthr-redis}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_PASSWORD=${REDIS_PASSWORD:-}

QUEUE_CONNECTION=database
FILESYSTEM_DISK=local
EOF

echo "Waiting for database..."
until (echo > /dev/tcp/${DB_HOST}/3306) 2>/dev/null; do
    echo "DB not ready, retrying in 3s..."
    sleep 3
done
echo "Database is ready!"


echo "Running migrations..."
if ! php /var/www/smartrh/artisan migrate --force --no-interaction; then
    echo "WARNING: migrate exited with an error, continuing startup..."
fi
echo "Checking if seeding needed..."
USER_COUNT=$(php /var/www/smartrh/artisan tinker \
    --execute="echo \App\Models\User::count();" 2>/dev/null | tail -1 | tr -d '[:space:]')
if [ "$USER_COUNT" = "0" ] || [ -z "$USER_COUNT" ]; then
    echo "Seeding database..."
    php /var/www/smartrh/artisan db:seed --force --no-interaction
else
    echo "Users already exist, skipping seeding."
fi


echo "Caching config..."
php /var/www/smartrh/artisan config:cache
php /var/www/smartrh/artisan route:cache

echo "Starting PHP-FPM..."
exec php-fpm