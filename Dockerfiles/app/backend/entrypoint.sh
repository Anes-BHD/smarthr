#!/bin/bash
set -e

echo "=== SmartHR Backend Entrypoint ==="

# ── 1. Permissions ────────────────────────────────────────────────────────────
echo "[1/7] Setting permissions..."
chmod -R 775 /var/www/smartrh/storage /var/www/smartrh/bootstrap/cache
chown -R www-data:www-data /var/www/smartrh/storage /var/www/smartrh/bootstrap/cache

# ── 2. Write .env from container environment variables ────────────────────────
echo "[2/7] Writing .env..."
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

# ── 3. Wait for MySQL to be ready (TCP check) ─────────────────────────────────
echo "[3/7] Waiting for database at ${DB_HOST}:3306..."
RETRIES=30
until (echo > /dev/tcp/${DB_HOST}/3306) 2>/dev/null; do
    RETRIES=$((RETRIES - 1))
    if [ "$RETRIES" -le 0 ]; then
        echo "ERROR: Database never became ready. Aborting."
        exit 1
    fi
    echo "  DB not ready, retrying in 3s... (${RETRIES} attempts left)"
    sleep 3
done
echo "  Database is ready!"

# ── 4. Run migrations ─────────────────────────────────────────────────────────
echo "[4/7] Running migrations..."

# Optional: Wipe database if DB_WIPE=true is set in ECS environment
if [ "${DB_WIPE}" = "true" ]; then
    echo "  DB_WIPE is true — wiping database..."
    php /var/www/smartrh/artisan db:wipe --force --no-interaction
fi

php /var/www/smartrh/artisan migrate --force --no-interaction
php /var/www/smartrh/artisan module:migrate --force --no-interaction
echo "  Migrations complete."

# Clear cache to ensure fresh state
php /var/www/smartrh/artisan optimize:clear

# ── 5. Seed only if the departments table is empty (raw PDO) ──────────────────
echo "[5/7] Checking if database needs seeding..."
DATA_EXISTS=$(php -r "
try {
    \$pdo = new PDO(
        'mysql:host=${DB_HOST};port=${DB_PORT:-3306};dbname=${DB_DATABASE}',
        '${DB_USERNAME}',
        '${DB_PASSWORD}'
    );
    // Check if departments table exists and has data
    \$res = \$pdo->query('SELECT COUNT(*) FROM departments')->fetchColumn();
    echo (\$res > 0) ? 'true' : 'false';
} catch (Exception \$e) {
    echo 'false';
}" 2>/dev/null || echo "false")

if [ "$DATA_EXISTS" = "false" ]; then
    echo "  Database is empty or missing core data — seeding now..."
    php /var/www/smartrh/artisan db:seed --force --no-interaction
    php /var/www/smartrh/artisan module:seed --force --no-interaction
    echo "  Seeding complete."
else
    echo "  Data already exists — skipping seed."
fi



# ── 6. Create storage symlink (public/storage → storage/app/public) ───────────
echo "[6/7] Creating storage symlink..."
php /var/www/smartrh/artisan storage:link --force || true

# ── 7. Cache config & routes for production performance ──────────────────────
echo "[7/7] Caching config and routes..."
php /var/www/smartrh/artisan config:cache
php /var/www/smartrh/artisan route:cache
php /var/www/smartrh/artisan view:cache

echo "=== Starting PHP-FPM ==="
exec php-fpm