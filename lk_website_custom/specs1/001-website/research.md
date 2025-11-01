# Research Findings: Lục Khí Website Platform

**Date**: 2025-10-29  
**Purpose**: Technical research to resolve implementation unknowns for Odoo CE 18 website platform

## Module Dependencies and Architecture

### Core Odoo CE 18 Modules

**Required Modules with Versions:**
- `website_slides` v2.7 - E-learning platform with video, quizzes, gamification
- `website_crm` v2.1 - Lead generation from website forms  
- `website_sale` v1.1 - E-commerce with payment integration
- `website_blog` v1.1 - Blog publishing and content management
- `l10n_vn` v2.0.3 - Vietnamese localization and accounting standards

**Module Dependency Hierarchy:**
```
Core Foundation: web → website → website_mail → website_partner → website_profile
Application Layer: website_blog, website_crm → website_slides, website_sale
Localization: l10n_vn
```

**Recommended OCA Enhancements:**
- `website_google_tag_manager` - Analytics integration
- `website_legal_page` - Legal compliance pages  
- `website_search_header` - Enhanced search functionality
- `auditlog` - Security and activity tracking
- `auto_backup` - Database backup automation

### Installation Order
1. Core foundation modules (web, website, etc.)
2. Communication modules (website_mail, website_partner)
3. Content modules (website_blog, website_crm)
4. Commerce modules (website_slides, website_sale)
5. Localization (l10n_vn)
6. OCA enhancements

## Vietnamese SEO Implementation

### URL Structure and Encoding
- Use UTF-8 encoding for Vietnamese characters in URLs
- Implement hyphen-separated Vietnamese URLs: `/khoa-hoc/luc-khi/co-ban-tam-thuat`
- Percent-encoding for non-ASCII characters when necessary
- Descriptive Vietnamese URLs for better user experience

### Meta Tags Optimization
- Title tags under 60 characters with Vietnamese keywords at beginning
- Meta descriptions under 160 characters in natural Vietnamese
- Open Graph tags with Vietnamese locale: `og:locale="vi_VN"`
- Hreflang implementation for international versions

### Technical SEO Implementation
```xml
<!-- Vietnamese SEO optimized header in QWeb -->
<html t-att-lang="vi-VN" t-att-dir="ltr">
<meta charset="utf-8"/>
<meta name="language" content="Vietnamese"/>
<link rel="alternate" hreflang="vi-VN" href="https://luckhi.vn<t t-att-url="current_url"/>"/>
```

### Local SEO Considerations
- Optimize for Cốc Cốc (Vietnamese search engine) alongside Google
- Implement Zalo search functionality integration
- Google Business Profile with Vietnamese address and phone format
- Vietnamese business categories and local listings

## Payment Gateway Integration

### Payment Architecture
**Primary Methods:**
1. **Cash on Delivery (COD)** - Auto-confirm orders immediately
2. **Manual Bank Transfer** - Wire transfer with automated email instructions
3. **VNPay Integration** - Commercial module ($147.04) with QR code support
4. **ZaloPay Integration** - Commercial module ($147.04) for mobile payments

**Payment Module Structure:**
```python
class LukiPaymentProvider(models.Model):
    _inherit = 'payment.provider'
    
    vietnam_gateway_type = fields.Selection([
        ('vnpay', 'VNPay'),
        ('zalopay', 'ZaloPay'), 
        ('cod', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
    ])
```

### Vietnamese Currency Handling
- VND with 0 decimal places (no cents)
- Currency symbol: ₫ positioned after amount
- Proper formatting for Vietnamese market
- Cash rounding for VND transactions

### Order Processing Workflows
- COD orders: Auto-confirm immediately
- Digital payments: Wait for webhook confirmation
- Bank transfers: Set to "waiting_payment" state
- Automated invoice generation with Vietnamese tax compliance

## Theme Development Strategy

### Custom Theme vs Extension
**Decision**: Create custom theme `luc_khi_theme` for:
- Complete control over Vietnamese typography
- Traditional Vietnamese aesthetic integration
- Optimized performance for specific use case
- Brand consistency across all modules

### Vietnamese Typography Optimization
- Primary fonts: Roboto (Latin) + Noto Sans Vietnamese
- Fallback fonts for Vietnamese diacritical marks
- Web font loading optimization for Vietnamese characters
- Line height and spacing optimized for Vietnamese text

### Theme Structure
```
luc_khi_theme/
├── static/
│   ├── src/
│   │   ├── scss/
│   │   │   ├── primary_variables.scss
│   │   │   ├── bootstrap_overridden.scss
│   │   │   └── custom_components.scss
│   │   ├── js/
│   │   └── img/
│   └── less/
├── views/
│   ├── assets.xml
│   └── templates.xml
└── __manifest__.py
```

### Design System
- Color palette inspired by traditional Vietnamese medicine
- Responsive design optimized for Vietnamese mobile users
- Accessibility compliance for Vietnamese content
- Performance-optimized asset loading

## Performance Optimization

### Caching Strategy
**Redis Configuration:**
- Session storage: `redis_session_store = True`
- Page caching: `ir_http_cache = True` with 1-hour TTL
- Static asset caching: 1-year expiration with immutable headers
- Database query result caching for frequently accessed data

### Video Content Delivery
**CDN Integration:**
- External video storage with signed URLs
- HLS streaming for adaptive bitrate
- Thumbnail generation and optimization
- Range request support for video streaming

### Database Optimization
**PostgreSQL Configuration:**
- `shared_buffers = 256MB` for 100+ concurrent users
- `effective_cache_size = 1GB`
- `work_mem = 16MB` per connection
- Connection pooling with `max_connections = 200`

**Critical Indexes:**
```sql
CREATE INDEX CONCURRENTLY idx_res_users_login ON res_users(login);
CREATE INDEX CONCURRENTLY idx_website_page_published ON website_page(website_published_date DESC);
CREATE INDEX CONCURRENTLY idx_slide_category_published ON slide_slide(category_id, website_published);
```

### Load Balancing Configuration
**Multi-Worker Setup:**
- Workers: `(CPU cores * 2) + 1` = 17 for 8-core server
- Memory limit: 2GB per worker hard, 1.25GB soft
- Dedicated cron workers: 2 threads
- Gevent for live chat functionality

## Security and Compliance

### Vietnamese Data Protection
- GDPR-inspired data handling practices
- Vietnamese customer data storage compliance
- Secure payment processing with PCI DSS considerations
- Regular security audits and penetration testing

### Access Control
- Role-based permissions for students vs public users
- Secure API endpoints with proper authentication
- Rate limiting for form submissions and login attempts
- IP-based access restrictions for admin areas

## Implementation Recommendations

### Phase 1: Foundation (Week 1-2)
1. Install core Odoo modules with Vietnamese localization
2. Set up Redis caching and PostgreSQL optimization
3. Configure basic Nginx reverse proxy
4. Implement custom theme foundation

### Phase 2: Core Features (Week 3-4)  
1. Develop custom modules (website, courses, blog, shop, CRM)
2. Implement Vietnamese SEO optimization
3. Set up payment gateway integration
4. Configure basic performance monitoring

### Phase 3: Optimization (Week 5-6)
1. Implement CDN for static assets and videos
2. Set up advanced caching strategies
3. Configure load balancing for high traffic
4. Performance testing and fine-tuning

## Key Configuration Files

### Odoo Configuration
```ini
[options]
db_host = localhost
db_port = 5432
db_maxconn = 64
workers = 17
limit_memory_hard = 2147483648
limit_memory_soft = 1342177280
proxy_mode = True
redis_session_store = True
cache_redis = True
```

### Nginx Production Setup
```nginx
server {
    listen 443 ssl http2;
    server_name luckhi.vn;
    
    # Static assets with long caching
    location ~* ^/[^/]+/static/.*$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Video streaming optimization
    location /videos/ {
        proxy_cache_valid 200 30d;
        add_header Accept-Ranges bytes;
    }
}
```

## Success Metrics and Monitoring

### Performance Targets
- Page load time: < 3 seconds (mobile)
- Concurrent users: 100+ without degradation
- Cache hit rate: > 80%
- Database connection usage: < 80%
- Error rate: < 1%

### Monitoring Setup
- Prometheus metrics collection
- Custom Odoo performance monitoring
- Real-time user experience tracking
- Automated alerting for performance issues

This research provides a comprehensive foundation for implementing the Lục Khí website platform with optimal performance, Vietnamese market optimization, and scalable architecture.
