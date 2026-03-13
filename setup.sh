#!/bin/bash
set -e

sudo apt install composer -y
sudo apt install npm -y
echo "==> Fixing vendor directory permissions..."
sudo chown -R "$USER:$USER" ~/smarthr/vendor 2>/dev/null || true
mkdir -p ~/smarthr/vendor

echo "==> Installing required PHP extensions..."
sudo apt install -y php8.3-bcmath php8.3-xml php8.3-gd

echo "==> Installing PHP dependencies..."
cd ~/smarthr
composer install --no-dev

echo "==> Installing Node dependencies..."
npm install

echo "==> Building frontend assets..."
npm run build

echo ""
echo "✅ Setup complete!"
