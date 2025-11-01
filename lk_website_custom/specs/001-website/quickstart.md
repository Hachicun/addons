# Quickstart Guide: Lục Khí Website Platform

**Date**: 2025-10-29  
**Version**: 1.0  
**Target Audience**: Developers and System Administrators

## Prerequisites

### System Requirements

**Hardware:**
- CPU: 8+ cores (16+ recommended for production)
- RAM: 16GB minimum (32GB+ recommended)
- Storage: 500GB SSD (1TB+ recommended)
- Network: 1Gbps+ bandwidth

**Software:**
- Ubuntu 20.04+ or CentOS 8+
- Python 3.11
- PostgreSQL 16
- Redis 6.0+
- Nginx 1.18+
- Node.js 18+ (for asset building)

### Odoo Dependencies

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-dev python3-pip
sudo apt install -y postgresql-16 postgresql-contrib
sudo apt install -y redis-server nginx
sudo apt install -y build-essential libpq-dev libxml2-dev libxslt1-dev
sudo apt install -y libldap2-dev libsasl2-dev libtiff5-dev libjpeg-dev
sudo apt install -y libopenjp2-7-dev zlib1g-dev libfreetype6-dev
sudo apt install -y liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev
sudo apt install -y libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev
```

## Installation

### 1. Database Setup

```bash
# Create PostgreSQL user
sudo -u postgres createuser --createdb --username postgres --pwprompt odoo
# Enter password when prompted

# Create database
sudo -u postgres createdb --username postgres --owner odoo luckhi_website
```

### 2. Redis Configuration

```bash
# Configure Redis for session storage
sudo nano /etc/redis/redis.conf
```

Add/modify these settings:
```ini
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

```bash
# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### 3. Odoo Installation

```bash
# Create Odoo user
sudo useradd -m -s /bin/bash odoo
sudo usermod -aG sudo odoo

# Clone Odoo 18
cd /opt
sudo git clone https://github.com/odoo/odoo.git --depth 1 --branch 18.0 odoo
sudo chown -R odoo:odoo odoo

# Install Python dependencies
cd /opt/odoo
sudo -u odoo python3 -m pip install -r requirements.txt
```

### 4. Lục Khí Modules Installation

```bash
# Navigate to addons directory
cd /opt/odoo/addons

# Clone Lục Khí custom modules
sudo -u odoo git clone https://github.com/your-org/lk_website_custom.git

# Install OCA modules (optional but recommended)
sudo -u odoo git clone https://github.com/OCA/website.git --depth 1 --branch 18.0 oca_website
sudo -u odoo git clone https://github.com/OCA/server-tools.git --depth 1 --branch 18.0 oca_server_tools
sudo -u odoo git clone https://github.com/OCA/l10n-vietnam.git --depth 1 --branch 18.0 oca_l10n_vietnam
```

### 5. Configuration

Create Odoo configuration file:
```bash
sudo nano /etc/odoo.conf
```

```ini
[options]
; Database
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_odoo_password
db_maxconn = 64
db_sslmode = require

; Server
addons_path = /opt/odoo/addons,/opt/odoo/odoo/addons
data_dir = /var/lib/odoo
logfile = /var/log/odoo/odoo.log
log_level = info
log_handler = INFO:file:/var/log/odoo/odoo.log

; Performance
workers = 17
limit_memory_hard = 2147483648
limit_memory_soft = 1342177280
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200

; Caching
proxy_mode = True
ir_http_cache = True
cache_redis = True
redis_host = localhost
redis_port = 6379
redis_db = 0
redis_cache_ttl = 86400

; Security
admin_passwd = your_admin_password
list_db = False
without_demo = True

; Modules to load
server_wide_modules = base,web,website,website_blog,website_slides,website_sale,website_crm,l10n_vn
```

### 6. Systemd Service

Create systemd service file:
```bash
sudo nano /etc/systemd/system/odoo.service
```

```ini
[Unit]
Description=Odoo 18
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=odoo
Group=odoo
WorkingDirectory=/opt/odoo
ExecStart=/usr/bin/python3 /opt/odoo/odoo-bin -c /etc/odoo.conf
StandardOutput=journal
StandardError=journal
KillMode=mixed
TimeoutStopSec=30
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start Odoo service
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo
```

## Nginx Configuration

### 1. SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d luckhi.vn -d www.luckhi.vn
```

### 2. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/luckhi.vn
```

```nginx
server {
    listen 80;
    server_name luckhi.vn www.luckhi.vn;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name luckhi.vn www.luckhi.vn;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/luckhi.vn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/luckhi.vn/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client Upload Size
    client_max_body_size 100M;

    # Proxy Settings
    proxy_connect_timeout 600;
    proxy_send_timeout 600;
    proxy_read_timeout 600;
    send_timeout 600;

    # Static Files with Long Caching
    location ~* ^/[^/]+/static/.*$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip_static on;
        gzip_types text/css application/javascript image/svg+xml;
    }

    # Web Content
    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Long Polling
    location /longpolling {
        proxy_pass http://127.0.0.1:8072;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Error Pages
    error_page 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/luckhi.vn /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Initial Setup

### 1. Database Initialization

```bash
# Create new database with modules
sudo -u odoo /opt/odoo/odoo-bin -d luckhi_website -i base,web,website,l10n_vn --without-demo=all --stop-after-init

# Install Lục Khí modules
sudo -u odoo /opt/odoo/odoo-bin -d luckhi_website -i luc_khi_website,luc_khi_courses,luc_khi_blog,luc_khi_shop,luc_khi_crm --stop-after-init
```

### 2. Admin Account Setup

1. Open browser: `https://luckhi.vn/web`
2. Create admin account:
   - Email: admin@luckhi.vn
   - Password: your chosen password
   - Company: Lục Khí
   - Country: Vietnam
   - Language: Vietnamese

### 3. Basic Configuration

#### Company Settings
1. Go to Settings → Companies → Lục Khí
2. Update company information:
   - Address: Your business address
   - Phone: Your business phone
   - Email: Your business email
   - Website: https://luckhi.vn

#### Vietnamese Localization
1. Go to Settings → General Settings → Localization
2. Set:
   - Language: Vietnamese
   - Currency: VND (Vietnamese Dong)
   - Timezone: Asia/Ho_Chi_Minh

#### Website Configuration
1. Go to Website → Configuration → Settings
2. Configure:
   - Website Domain: luckhi.vn
   - Default Language: Vietnamese
   - Google Analytics: Add tracking code
   - Enable SEO features

## Module Configuration

### 1. luc_khi_website

1. Go to Apps → luc_khi_website → Configuration
2. Set up:
   - Company information
   - Contact email
   - Social media links
   - Google Maps API key

### 2. luc_khi_courses

1. Go to Apps → luc_khi_courses → Configuration
2. Configure:
   - Course categories
   - Instructor profiles
   - Certificate templates
   - Email notifications

### 3. luc_khi_blog

1. Go to Apps → luc_khi_blog → Configuration
2. Set up:
   - Blog categories
   - Author profiles
   - Comment moderation
   - SEO settings

### 4. luc_khi_shop

1. Go to Apps → luc_khi_shop → Configuration
2. Configure:
   - Payment methods (COD, Bank Transfer, VNPay)
   - Shipping methods
   - Tax rates (VAT 10%, 5%, 0%)
   - Email templates

### 5. luc_khi_crm

1. Go to Apps → luc_khi_crm → Configuration
2. Set up:
   - Lead scoring rules
   - Email templates
   - Follow-up schedules
   - Sales pipeline stages

## Content Creation

### 1. Create Sample Course

1. Go to Lục Khí → Courses → Create
2. Fill in course information:
   - Name: "Lục Khí Cơ Bản"
   - Level: "Cơ Bản"
   - Price: 1,500,000 VND
   - Description: Course description in Vietnamese
3. Add course image and intro video
4. Create slide channel and add content
5. Publish course

### 2. Create Blog Posts

1. Go to Website → Blog → New
2. Create sample posts:
   - "Lục Khí là gì?"
   - "Lợi ích của Lục Khí"
   - "Học Lục Khí như thế nào?"
3. Add Vietnamese content, images, and SEO metadata
4. Publish posts

### 3. Add Products

1. Go to Products → Create
2. Add sample products:
   - Books about Lục Khí
   - Consultation services
   - Course enrollments
3. Set prices in VND
4. Add Vietnamese descriptions
5. Publish products

## Testing

### 1. Functionality Testing

```bash
# Test all modules
curl -I https://luckhi.vn/
curl -I https://luckhi.vn/courses
curl -I https://luckhi.vn/blog
curl -I https://luckhi.vn/shop
curl -I https://luckhi.vn/contact
```

### 2. Performance Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test homepage performance
ab -n 100 -c 10 https://luckhi.vn/

# Test API endpoints
ab -n 100 -c 10 https://luckhi.vn/api/v1/courses
```

### 3. SSL Certificate

```bash
# Test SSL configuration
sudo certbot certificates
sudo openssl s_client -connect luckhi.vn:443
```

## Monitoring

### 1. Log Monitoring

```bash
# View Odoo logs
sudo tail -f /var/log/odoo/odoo.log

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View system logs
sudo journalctl -u odoo -f
```

### 2. Performance Monitoring

```bash
# Check system resources
htop
df -h
free -h

# Check Odoo processes
ps aux | grep odoo

# Check database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

## Backup Strategy

### 1. Database Backup

```bash
# Create backup script
sudo nano /usr/local/bin/backup-odoo.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/odoo"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="luckhi_website"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Backup filestore
tar -czf $BACKUP_DIR/filestore_backup_$DATE.tar.gz /var/lib/odoo/filestore/$DB_NAME

# Remove old backups (keep 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/backup-odoo.sh

# Add to crontab
sudo crontab -e
```

Add line:
```
0 2 * * * /usr/local/bin/backup-odoo.sh
```

## Troubleshooting

### Common Issues

1. **Odoo won't start**
   - Check logs: `sudo journalctl -u odoo`
   - Verify configuration: `sudo -u odoo /opt/odoo/odoo-bin -c /etc/odoo.conf --stop-after-init`
   - Check database connection

2. **Module installation fails**
   - Check dependencies in `__manifest__.py`
   - Verify Python packages are installed
   - Check file permissions

3. **Performance issues**
   - Check worker configuration
   - Verify Redis is running
   - Monitor database performance

4. **SSL certificate issues**
   - Check certificate expiration: `sudo certbot certificates`
   - Verify Nginx configuration
   - Test SSL configuration

### Support Resources

- Odoo Documentation: https://www.odoo.com/documentation
- Lục Khí Development Team: dev@luckhi.vn
- System Monitoring: https://monitoring.luckhi.vn

## Next Steps

1. Configure production monitoring
2. Set up automated testing
3. Implement CI/CD pipeline
4. Configure CDN for static assets
5. Set up disaster recovery

This quickstart guide provides the foundation for deploying and managing the Lục Khí website platform in production.
