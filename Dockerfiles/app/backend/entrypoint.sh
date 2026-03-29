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
APP_URL=${APP_URL:-http://localhost}

LOG_CHANNEL=stderr
LOG_LEVEL=debug

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

echo "Checking migration status..."
TABLE_EXISTS=$(mysql -h "${DB_HOST}" -P "${DB_PORT:-3306}" \
    -u "${DB_USERNAME}" -p"${DB_PASSWORD}" \
    --skip-column-names --silent \
    -e "SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema='${DB_DATABASE}' 
        AND table_name='users';" 2>/dev/null || echo "0")

if [ "$TABLE_EXISTS" = "0" ]; then
    echo "Fresh database detected, running migrations..."
    php /var/www/smartrh/artisan migrate --force --no-interaction
    echo "Seeding database..."
    php /var/www/smartrh/artisan db:seed --force
else
    echo "Database already set up, skipping migrations..."
fi

echo "Caching config..."
php /var/www/smartrh/artisan config:cache
php /var/www/smartrh/artisan route:cache

echo "Starting PHP-FPM..."
exec php-fpm