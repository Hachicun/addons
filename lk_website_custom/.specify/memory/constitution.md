# Lục Khí Website Platform Constitution

## Core Principles

### I. Vietnamese-First Development
All user-facing content must be in Vietnamese; Vietnamese language support is mandatory for all modules; Vietnamese-friendly URL slugs and SEO optimization required; Cultural adaptation for Vietnamese users

### II. Modular Architecture
Each feature is implemented as independent Odoo module; Modules must be self-contained with proper MVC structure; Clear dependencies and data relationships; Independent testing and deployment capability

### III. User Story-Driven Development
All development follows user story methodology; Each user story broken into specific tasks; Tasks completed independently before moving to next story; User acceptance criteria defined upfront

### IV. SEO and Performance Optimization
All pages must have proper meta tags and SEO optimization; Vietnamese search engine compatibility (Google, Cốc Cốc); Mobile-first responsive design; Performance monitoring and optimization

### V. Security and Access Control
Proper access controls for all user roles; Input validation and sanitization; Secure data handling practices; Regular security audits and compliance

## Module Architecture

### Core Website Module (luc_khi_website)
Foundation module providing basic website functionality; Homepage, About, Contact pages; Team member management; Basic SEO and responsive design

### E-Learning Module (luc_khi_courses)
Course management and enrollment system; Vietnamese course content support; Student progress tracking; Integration with website_slides for video content

### Blog Module (luc_khi_blog)
Enhanced blog functionality with Vietnamese categories; SEO optimization and social sharing; Blog-course cross-linking; Vietnamese-friendly URL generation

### E-Commerce Module (luc_khi_shop)
Product catalog and shopping cart; Vietnamese payment gateway integration; Order management and tracking; Product recommendations based on Lục Khí

### CRM Module (luc_khi_crm)
Contact form management; Lead generation and tracking; Vietnamese contact methods; Integration with email marketing

## Development Standards

### Code Quality
Follow Odoo coding standards; Comprehensive documentation; Unit and integration testing; Code review mandatory for all changes

### Vietnamese Localization
Proper Vietnamese character encoding; Date/time formatting for Vietnam; Currency support (VND); Vietnamese address and phone number formats

### Performance Standards
Page load times under 3 seconds; Mobile performance optimization; Database query optimization; Caching strategies implementation

## Security Requirements

### Data Protection
Compliance with Vietnamese data protection laws; Secure user data storage; Regular security updates; Access logging and monitoring

### Input Validation
All user inputs validated and sanitized; XSS and SQL injection prevention; Secure file upload handling; Rate limiting implementation

## Deployment and Operations

### Environment Management
Separate development, staging, and production environments; Automated testing and deployment; Database backup and recovery; Performance monitoring and alerting

### Quality Assurance
Automated testing pipeline; User acceptance testing; Cross-browser compatibility testing; Mobile device testing

## Governance

### Module Management
Each module has clear ownership and responsibility; Module dependencies properly documented; Version control and change management; Regular module updates and maintenance

### User Story Management
User stories prioritized by business value; Task completion tracked and reported; Regular stakeholder reviews and feedback; Continuous improvement process

**Version**: 1.0.0 | **Ratified**: 2025-10-29 | **Last Amended**: 2025-10-29