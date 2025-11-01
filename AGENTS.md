# Agent Context for Lục Khí Website Platform

**Last Updated**: 2025-10-29  
**Project**: Lục Khí Website Platform (001-website)

## Technology Stack

### Core Technologies
- **Language**: Python 3.11
- **Framework**: Odoo CE 18
- **Database**: PostgreSQL 16
- **Web Server**: Nginx
- **Cache**: Redis 6.0+
- **Project Type**: Web application (Odoo module-based architecture)

### Odoo Modules
- **Core**: website, website_sale, website_blog, website_slides, website_crm
- **Localization**: l10n_vn (Vietnamese)
- **Custom Modules**: luc_khi_website, luc_khi_courses, luc_khi_blog, luc_khi_shop, luc_khi_crm
- **OCA Modules**: website_google_tag_manager, website_legal_page, website_search_header, auditlog, auto_backup

### Frontend Technologies
- **Templating**: QWeb (Odoo's template engine)
- **CSS Framework**: Bootstrap 5 (Odoo default)
- **JavaScript**: jQuery, Odoo's web framework
- **Responsive Design**: Mobile-first approach

### Development Tools
- **Version Control**: Git
- **Package Management**: pip (Python)
- **Testing**: Odoo test framework, pytest
- **Code Quality**: Pylint, Black (Python formatter)

### Infrastructure
- **Operating System**: Ubuntu 20.04+ / CentOS 8+
- **Containerization**: Docker (optional)
- **Monitoring**: Prometheus, Grafana
- **Logging**: Structured logging with log rotation

## Vietnamese Localization

### Language Support
- **Primary Language**: Vietnamese (vi_VN)
- **Character Encoding**: UTF-8
- **URL Structure**: Vietnamese-friendly slugs with hyphens
- **Date Format**: DD/MM/YYYY
- **Time Format**: 24-hour
- **Currency**: VND (₫)

### SEO Considerations
- **Search Engines**: Google, Cốc Cốc (Vietnamese)
- **Meta Tags**: Vietnamese titles and descriptions
- **Social Media**: Zalo integration
- **Local SEO**: Google Business Profile for Vietnam

## Development Guidelines

### Code Standards
- Follow Odoo coding standards
- Use Vietnamese for user-facing strings
- Implement proper error handling
- Write comprehensive tests
- Document all custom modules

### Security Best Practices
- Implement proper access controls
- Validate all user inputs
- Use HTTPS everywhere
- Implement rate limiting
- Regular security audits

### Performance Optimization
- Implement Redis caching
- Optimize database queries
- Use CDN for static assets
- Implement lazy loading
- Monitor Core Web Vitals

## Module Architecture

### Custom Modules Structure
```
luc_khi_website/     # Core website functionality
luc_khi_courses/     # E-learning platform
luc_khi_blog/        # Enhanced blog functionality
luc_khi_shop/        # E-commerce enhancements
luc_khi_crm/         # CRM form integration
luc_khi_theme/       # Custom theme (optional)
```

### Data Models
- Course management with Vietnamese content
- Enhanced blog with categorization
- Product catalog with Vietnamese compliance
- Lead management with Vietnamese contact methods
- Website content management

### API Design
- RESTful APIs following OpenAPI 3.0
- Vietnamese language support
- Proper error handling
- Rate limiting and security
- Comprehensive documentation

## Testing Strategy

### Unit Testing
- Model methods and business logic
- Vietnamese content handling
- Data validation
- Edge cases

### Integration Testing
- Module interactions
- Payment gateway integration
- Email notifications
- Third-party service integration

### End-to-End Testing
- User workflows in Vietnamese
- Mobile responsiveness
- Performance under load
- Cross-browser compatibility

## Deployment

### Environment Setup
- Development: Local Odoo instance
- Staging: Production-like environment
- Production: High-availability setup

### CI/CD Pipeline
- Automated testing
- Code quality checks
- Security scanning
- Automated deployment

### Monitoring
- Application performance monitoring
- Error tracking
- User experience metrics
- Business intelligence

## Compliance

### Vietnamese Regulations
- Data protection laws
- E-commerce regulations
- Tax compliance (VAT)
- Consumer protection

### International Standards
- GDPR-inspired data handling
- PCI DSS for payments
- Web accessibility (WCAG)
- Security best practices

## Support and Maintenance

### Documentation
- User manuals in Vietnamese
- Developer documentation
- API documentation
- Troubleshooting guides

### Support Channels
- Email support
- Phone support (Vietnamese)
- Zalo integration
- Online help center

### Maintenance Schedule
- Regular updates
- Security patches
- Performance optimization
- Feature enhancements

This context should be used when working on any aspect of the Lục Khí website platform to ensure consistency and adherence to project standards.
