# Data Model: Lục Khí Website Platform

**Date**: 2025-10-29  
**Purpose**: Define data entities and relationships for Odoo custom modules

## Core Data Models

### 1. Course Management (luc_khi_courses)

#### luc_khi.course
```python
class LucKhiCourse(models.Model):
    _name = 'luc_khi.course'
    _description = 'Lục Khí Course'
    _order = 'sequence, name'
    
    # Basic Information
    name = fields.Char('Course Name', required=True, translate=True)
    description = fields.Html('Description', translate=True)
    short_description = fields.Text('Short Description', translate=True)
    
    # Course Structure
    level = fields.Selection([
        ('basic', 'Cơ Bản'),
        ('intermediate_1', 'Trung Cấp 1'),
        ('intermediate_2', 'Trung Cấp 2'), 
        ('intermediate_3', 'Trung Cấp 3'),
        ('advanced', 'Nâng Cao'),
    ], required=True, default='basic')
    
    sequence = fields.Integer('Sequence', default=10)
    
    # Media and Content
    image = fields.Image('Course Image')
    video_url = fields.Char('Introduction Video URL')
    slide_channel_id = fields.Many2one(
        'slide.channel', 
        string='Slide Channel',
        help='Connected slide channel for course content'
    )
    
    # Pricing and Sales
    price = fields.Monetary('Price', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    # Access Control
    is_published = fields.Boolean('Published', default=False)
    access_mode = fields.Selection([
        ('public', 'Public'),
        ('registered', 'Registered Users'),
        ('purchased', 'Purchased Only'),
    ], default='purchased')
    
    # Metadata
    duration_hours = fields.Float('Duration (Hours)')
    difficulty_level = fields.Integer('Difficulty Level (1-10)')
    prerequisites = fields.Text('Prerequisites', translate=True)
    learning_objectives = fields.Html('Learning Objectives', translate=True)
    
    # SEO and Marketing
    seo_title = fields.Char('SEO Title', translate=True)
    seo_description = fields.Text('SEO Description', translate=True)
    slug = fields.Char('URL Slug', compute='_compute_slug', store=True)
    
    # Relations
    category_id = fields.Many2one('luc_khi.course.category', string='Category')
    instructor_ids = fields.Many2many('res.partner', string='Instructors')
    tag_ids = fields.Many2many('luc_khi.course.tag', string='Tags')
    
    _sql_constraints = [
        ('slug_unique', 'unique(slug)', 'URL slug must be unique!'),
    ]
    
    @api.depends('name')
    def _compute_slug(self):
        for course in self:
            if course.name:
                course.slug = self._generate_slug(course.name)
    
    def _generate_slug(self, text):
        # Vietnamese-friendly slug generation
        import re
        text = text.lower()
        # Vietnamese character normalization
        replacements = {
            'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'đ': 'd',
            'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        }
        for viet_char, latin_char in replacements.items():
            text = text.replace(viet_char, latin_char)
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')
```

#### luc_khi.course.category
```python
class LucKhiCourseCategory(models.Model):
    _name = 'luc_khi.course.category'
    _description = 'Course Category'
    _order = 'name'
    
    name = fields.Char('Category Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    parent_id = fields.Many2one('luc_khi.course.category', string='Parent Category')
    child_ids = fields.One2many('luc_khi.course.category', 'parent_id', string='Child Categories')
    course_ids = fields.One2many('luc_khi.course', 'category_id', string='Courses')
    sequence = fields.Integer('Sequence', default=10)
    is_published = fields.Boolean('Published', default=True)
```

#### luc_khi.course.tag
```python
class LucKhiCourseTag(models.Model):
    _name = 'luc_khi.course.tag'
    _description = 'Course Tag'
    _order = 'name'
    
    name = fields.Char('Tag Name', required=True, translate=True)
    color = fields.Integer('Color Index', default=0)
    course_ids = fields.Many2many('luc_khi.course', column_name='course_tag_rel')
```

### 2. Blog Enhancement (luc_khi_blog)

#### blog.post (Extended)
```python
class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    # Enhanced categorization
    luc_khi_category = fields.Selection([
        ('knowledge', 'Kiến thức'),
        ('testimonial', 'Testimonial'),
        ('lifestyle', 'Lối sống'),
        ('community', 'Cộng đồng'),
        ('news', 'Tin tức'),
    ], string='Lục Khí Category')
    
    # Enhanced SEO
    meta_title = fields.Char('Meta Title', translate=True)
    meta_description = fields.Text('Meta Description', translate=True)
    focus_keyword = fields.Char('Focus Keyword', translate=True)
    
    # Content relationships
    related_course_ids = fields.Many2many('luc_khi.course', string='Related Courses')
    related_event_ids = fields.Many2many('event.event', string='Related Events')
    
    # Enhanced media
    cover_image = fields.Image('Cover Image')
    author_bio = fields.Html('Author Bio', translate=True)
    reading_time = fields.Integer('Reading Time (Minutes)', compute='_compute_reading_time')
    
    # Series functionality (v2)
    series_id = fields.Many2one('blog.series', string='Series')
    series_sequence = fields.Integer('Sequence in Series')
    
    @api.depends('content')
    def _compute_reading_time(self):
        words_per_minute = 200  # Average reading speed
        for post in self:
            if post.content:
                # Strip HTML tags and count words
                import re
                text = re.sub(r'<[^>]+>', '', post.content)
                word_count = len(text.split())
                post.reading_time = max(1, round(word_count / words_per_minute))
            else:
                post.reading_time = 1
```

#### blog.series (New Model)
```python
class BlogSeries(models.Model):
    _name = 'blog.series'
    _description = 'Blog Post Series'
    _order = 'name'
    
    name = fields.Char('Series Name', required=True, translate=True)
    description = fields.Html('Description', translate=True)
    post_ids = fields.One2many('blog.post', 'series_id', string='Posts')
    is_published = fields.Boolean('Published', default=True)
    sequence = fields.Integer('Sequence', default=10)
```

### 3. E-commerce Enhancement (luc_khi_shop)

#### product.template (Extended)
```python
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Lục Khí specific fields
    luc_khi_type = fields.Selection([
        ('book', 'Sách'),
        ('service', 'Dịch vụ'),
        ('course', 'Khóa học'),
        ('medicine', 'Thuốc'),
        ('tool', 'Dụng cụ'),
    ], string='Lục Khí Product Type')
    
    # Enhanced content
    detailed_description = fields.Html('Detailed Description', translate=True)
    usage_instructions = fields.Html('Usage Instructions', translate=True)
    ingredients = fields.Text('Ingredients', translate=True)  # For medicines
    contraindications = fields.Text('Contraindications', translate=True)
    
    # Course integration
    course_id = fields.Many2one('luc_khi.course', string='Related Course')
    auto_grant_access = fields.Boolean('Auto Grant Course Access', default=True)
    
    # Service scheduling
    is_service = fields.Boolean('Is Service')
    service_duration = fields.Float('Service Duration (Hours)')
    requires_appointment = fields.Boolean('Requires Appointment')
    
    # Vietnamese compliance
    gtn_number = fields.Char('GTN Number')  # Giấy thông báo
    announcement_number = fields.Char('Announcement Number')
    manufacturer = fields.Char('Manufacturer', translate=True)
    origin = fields.Char('Origin', translate=True)
```

### 4. CRM Enhancement (luc_khi_crm)

#### crm.lead (Extended)
```python
class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    # Enhanced lead categorization
    lead_type = fields.Selection([
        ('course_inquiry', 'Khóa học'),
        ('medical_consultation', 'Khám bệnh'),
        ('book_inquiry', 'Sách'),
        ('general_info', 'Thông tin chung'),
        ('partnership', 'Hợp tác'),
    ], string='Lead Type', required=True)
    
    # Source tracking
    source_page = fields.Char('Source Page')
    utm_campaign = fields.Char('UTM Campaign')
    utm_source = fields.Char('UTM Source')
    utm_medium = fields.Char('UTM Medium')
    
    # Vietnamese specific fields
    zalo_phone = fields.Char('Zalo Phone')
    preferred_contact_method = fields.Selection([
        ('phone', 'Phone'),
        ('zalo', 'Zalo'),
        ('email', 'Email'),
        ('in_person', 'In Person'),
    ], default='phone')
    
    # Course interest tracking
    interested_courses = fields.Many2many('luc_khi.course', string='Interested Courses')
    current_knowledge_level = fields.Selection([
        ('beginner', 'Mới bắt đầu'),
        ('some_knowledge', 'Có kiến thức cơ bản'),
        ('intermediate', 'Trung cấp'),
        ('advanced', 'Nâng cao'),
    ], string='Current Knowledge Level')
    
    # Follow-up automation
    last_email_sent = fields.Datetime('Last Email Sent')
    email_count = fields.Integer('Email Count', default=0)
    next_follow_up = fields.Datetime('Next Follow Up')
    
    def action_schedule_follow_up(self):
        """Schedule automated follow-up based on lead type"""
        if self.lead_type == 'course_inquiry':
            # Send course information after 1 day
            self.next_follow_up = fields.Datetime.now() + timedelta(days=1)
        elif self.lead_type == 'medical_consultation':
            # Schedule consultation call within 24 hours
            self.next_follow_up = fields.Datetime.now() + timedelta(hours=24)
```

### 5. Website Content (luc_khi_website)

#### luc_khi.website.page
```python
class LucKhiWebsitePage(models.Model):
    _name = 'luc_khi.website.page'
    _description = 'Lục Khí Website Page'
    _order = 'sequence, name'
    
    name = fields.Char('Page Name', required=True, translate=True)
    title = fields.Char('Page Title', required=True, translate=True)
    content = fields.Html('Page Content', translate=True)
    
    # Page identification
    page_key = fields.Char('Page Key', required=True, help='Unique identifier for the page')
    is_published = fields.Boolean('Published', default=True)
    
    # SEO
    seo_title = fields.Char('SEO Title', translate=True)
    seo_description = fields.Text('SEO Description', translate=True)
    seo_keywords = fields.Char('SEO Keywords', translate=True)
    
    # Layout and display
    show_in_menu = fields.Boolean('Show in Menu', default=False)
    menu_sequence = fields.Integer('Menu Sequence', default=10)
    parent_menu_id = fields.Many2one('website.menu', string='Parent Menu')
    
    # Template
    view_id = fields.Many2one('ir.ui.view', string='Template')
    
    _sql_constraints = [
        ('page_key_unique', 'unique(page_key)', 'Page key must be unique!'),
    ]
```

#### luc_khi.team.member
```python
class LucKhiTeamMember(models.Model):
    _name = 'luc_khi.team.member'
    _description = 'Lục Khí Team Member'
    _order = 'sequence, name'
    
    name = fields.Char('Name', required=True, translate=True)
    position = fields.Char('Position', translate=True)
    bio = fields.Html('Biography', translate=True)
    
    # Media
    photo = fields.Image('Photo')
    
    # Contact
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    zalo = fields.Char('Zalo')
    
    # Expertise
    expertise = fields.Text('Areas of Expertise', translate=True)
    certifications = fields.Text('Certifications', translate=True)
    
    # Display
    is_published = fields.Boolean('Published', default=True)
    sequence = fields.Integer('Sequence', default=10)
    featured = fields.Boolean('Featured Member', default=False)
```

## Data Relationships and Constraints

### Key Relationships

1. **Course → Slide Channel**: Each course links to a slide.channel for e-learning content
2. **Course → Product**: Courses can be sold as products with automatic access granting
3. **Blog Post → Course**: Blog posts can reference related courses
4. **Lead → Course**: Leads can track interested courses for targeted marketing
5. **Product → Course**: Products can automatically grant course access upon purchase

### Data Integrity Constraints

1. **Unique Slugs**: All public-facing content must have unique URL slugs
2. **Published Content**: Only published content should be visible to public users
3. **Access Control**: Course access must be validated against user permissions
4. **Price Validation**: Course and product prices must be positive values
5. **Email Validation**: All email fields must be properly formatted

### State Transitions

#### Course Lifecycle
```
Draft → Published → Archived
   ↓         ↓         ↓
Hidden    Active    Inactive
```

#### Lead Management
```
New → Qualified → Converted → Won/Lost
  ↓       ↓         ↓        ↓
New    Working   Customer  Closed
```

#### Order Processing
```
Draft → Sent → Confirmed → Done/Cancelled
   ↓      ↓       ↓         ↓
New   Pending  Active   Complete
```

## Performance Considerations

### Database Indexing Strategy
```sql
-- Course-related indexes
CREATE INDEX idx_luc_khi_course_published ON luc_khi_course(is_published, sequence);
CREATE INDEX idx_luc_khi_course_category ON luc_khi_course(category_id, is_published);
CREATE INDEX idx_luc_khi_course_level ON luc_khi_course(level, is_published);

-- Blog-related indexes
CREATE INDEX idx_blog_post_published ON blog_post(website_published, post_date);
CREATE INDEX idx_blog_post_category ON blog_post(luc_khi_category, website_published);

-- Lead-related indexes
CREATE INDEX idx_crm_lead_type ON crm_lead(type, create_date);
CREATE INDEX idx_crm_lead_followup ON crm_lead(next_follow_up, lead_type);

-- Product-related indexes
CREATE INDEX idx_product_template_luc_khi_type ON product_template(luc_khi_type, sale_ok);
```

### Data Archiving Strategy
- Archive completed orders after 2 years
- Archive converted leads after 1 year
- Archive old blog drafts after 6 months
- Keep course data indefinitely for compliance

## Security and Access Control

### Role-Based Permissions

1. **Public Users**: Can view published courses, blog posts, and products
2. **Registered Users**: Can access purchased courses and comment on blog
3. **Students**: Can access enrolled courses and track progress
4. **Instructors**: Can manage course content and student progress
5. **Administrators**: Full access to all content and settings

### Data Privacy
- Encrypt sensitive personal information
- Implement data retention policies
- Provide user data export functionality
- Comply with Vietnamese data protection regulations

This data model provides a comprehensive foundation for the Lục Khí website platform with proper relationships, constraints, and performance optimizations.
