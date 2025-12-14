FROM php:8.2-fpm

# Set working directory
WORKDIR /var/www/smartrh

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    libzip-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libicu-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) \
    pdo_mysql \
    mbstring \
    exif \
    pcntl \
    bcmath \
    gd \
    zip \
    intl \
    opcache

# Install Redis extension
RUN pecl install redis && docker-php-ext-enable redis

# Install wkhtmltopdf for PDF generation
# Required by: barryvdh/laravel-snappy package
# Used for: PDF exports in DataTables (Client, Employee, Payslip, etc.) and estimate PDFs
RUN apt-get update && apt-get install -y \
    xvfb \
    xfonts-75dpi \
    xfonts-base \
    && wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-2.bullseye_amd64.deb || apt-get install -yf \
    && rm -rf /var/lib/apt/lists/* \
    && rm wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && ln -s /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf \
    && ln -s /usr/local/bin/wkhtmltoimage /usr/bin/wkhtmltoimage

# Configure PHP-FPM to listen on TCP port 9000
RUN echo "listen = 0.0.0.0:9000" >> /usr/local/etc/php-fpm.d/www.conf

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set proper permissions for Laravel
RUN chown -R www-data:www-data /var/www/smartrh

# Expose port 9000 for PHP-FPM
EXPOSE 9000

CMD ["php-fpm"]
