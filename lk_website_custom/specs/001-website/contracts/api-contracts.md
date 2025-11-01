# API Contracts: Lục Khí Website Platform

**Date**: 2025-10-29  
**Version**: 1.0  
**Format**: OpenAPI 3.0 specification

## Overview

This document defines the API contracts for the Lục Khí website platform, covering course management, blog functionality, e-commerce, and CRM integration. All APIs follow RESTful conventions and return JSON responses.

## Base Configuration

```yaml
openapi: 3.0.3
info:
  title: Lục Khí Website API
  description: API for Lục Khí traditional medicine education platform
  version: 1.0.0
  contact:
    name: Lục Khí Development Team
    email: dev@luckhi.vn
servers:
  - url: https://luckhi.vn/api/v1
    description: Production server
  - url: https://staging.luckhi.vn/api/v1
    description: Staging server
```

## Authentication

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    SessionAuth:
      type: apiKey
      in: cookie
      name: session_id
```

## Course Management APIs

### Get Course List

```yaml
paths:
  /courses:
    get:
      summary: Get list of published courses
      tags:
        - Courses
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: category
          in: query
          schema:
            type: string
        - name: level
          in: query
          schema:
            type: string
            enum: [basic, intermediate_1, intermediate_2, intermediate_3, advanced]
        - name: search
          in: query
          schema:
            type: string
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  courses:
                    type: array
                    items:
                      $ref: '#/components/schemas/Course'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
```

### Get Course Details

```yaml
  /courses/{courseId}:
    get:
      summary: Get detailed course information
      tags:
        - Courses
      parameters:
        - name: courseId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Course details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CourseDetail'
        '404':
          description: Course not found
```

### Enroll in Course

```yaml
    post:
      summary: Enroll user in course
      tags:
        - Courses
      security:
        - SessionAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                course_id:
                  type: integer
      responses:
        '200':
          description: Enrollment successful
        '401':
          description: Authentication required
        '403':
          description: Access denied
```

## Blog APIs

### Get Blog Posts

```yaml
  /blog/posts:
    get:
      summary: Get list of blog posts
      tags:
        - Blog
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
        - name: category
          in: query
          schema:
            type: string
            enum: [knowledge, testimonial, lifestyle, community, news]
        - name: tag
          in: query
          schema:
            type: string
      responses:
        '200':
          description: Blog posts list
          content:
            application/json:
              schema:
                type: object
                properties:
                  posts:
                    type: array
                    items:
                      $ref: '#/components/schemas/BlogPost'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
```

### Get Blog Post Details

```yaml
  /blog/posts/{postId}:
    get:
      summary: Get detailed blog post
      tags:
        - Blog
      parameters:
        - name: postId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Blog post details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BlogPostDetail'
```

## E-commerce APIs

### Get Products

```yaml
  /products:
    get:
      summary: Get list of products
      tags:
        - Products
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: category
          in: query
          schema:
            type: string
            enum: [book, service, course, medicine, tool]
        - name: search
          in: query
          schema:
            type: string
      responses:
        '200':
          description: Products list
          content:
            application/json:
              schema:
                type: object
                properties:
                  products:
                    type: array
                    items:
                      $ref: '#/components/schemas/Product'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
```

### Create Order

```yaml
    post:
      summary: Create new order
      tags:
        - Orders
      security:
        - SessionAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                lines:
                  type: array
                  items:
                    type: object
                    properties:
                      product_id:
                        type: integer
                      quantity:
                        type: integer
                payment_method:
                  type: string
                  enum: [cod, bank_transfer, vnpay, zalopay]
                shipping_address:
                  $ref: '#/components/schemas/Address'
      responses:
        '201':
          description: Order created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
```

## CRM APIs

### Submit Contact Form

```yaml
  /contact:
    post:
      summary: Submit contact form
      tags:
        - Contact
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                email:
                  type: string
                  format: email
                phone:
                  type: string
                zalo_phone:
                  type: string
                lead_type:
                  type: string
                  enum: [course_inquiry, medical_consultation, book_inquiry, general_info, partnership]
                message:
                  type: string
                interested_courses:
                  type: array
                  items:
                    type: integer
      responses:
        '201':
          description: Contact form submitted successfully
        '400':
          description: Invalid input data
```

## Data Schemas

### Course Schema

```yaml
components:
  schemas:
    Course:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        description:
          type: string
        short_description:
          type: string
        level:
          type: string
          enum: [basic, intermediate_1, intermediate_2, intermediate_3, advanced]
        image:
          type: string
          format: uri
        price:
          type: number
          format: float
        currency:
          type: string
        duration_hours:
          type: number
          format: float
        difficulty_level:
          type: integer
          minimum: 1
          maximum: 10
        slug:
          type: string
        category:
          $ref: '#/components/schemas/CourseCategory'
        instructors:
          type: array
          items:
            $ref: '#/components/schemas/Instructor'
        tags:
          type: array
          items:
            type: string
    
    CourseDetail:
      allOf:
        - $ref: '#/components/schemas/Course'
        - type: object
          properties:
            learning_objectives:
              type: string
            prerequisites:
              type: string
            video_url:
              type: string
              format: uri
            slide_channel_id:
              type: integer
            is_enrolled:
              type: boolean
            progress_percentage:
              type: number
              format: float
            related_courses:
              type: array
              items:
                $ref: '#/components/schemas/Course'
```

### Blog Schema

```yaml
    BlogPost:
      type: object
      properties:
        id:
          type: integer
        title:
          type: string
        subtitle:
          type: string
        summary:
          type: string
        cover_image:
          type: string
          format: uri
        published_date:
          type: string
          format: date-time
        author:
          $ref: '#/components/schemas/Author'
        luc_khi_category:
          type: string
          enum: [knowledge, testimonial, lifestyle, community, news]
        tags:
          type: array
          items:
            type: string
        reading_time:
          type: integer
        slug:
          type: string
    
    BlogPostDetail:
      allOf:
        - $ref: '#/components/schemas/BlogPost'
        - type: object
          properties:
            content:
              type: string
            author_bio:
              type: string
            related_courses:
              type: array
              items:
                $ref: '#/components/schemas/Course'
            related_events:
              type: array
              items:
                $ref: '#/components/schemas/Event'
            series:
              $ref: '#/components/schemas/BlogSeries'
```

### Product Schema

```yaml
    Product:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        description:
          type: string
        detailed_description:
          type: string
        price:
          type: number
          format: float
        currency:
          type: string
        image:
          type: string
          format: uri
        luc_khi_type:
          type: string
          enum: [book, service, course, medicine, tool]
        is_available:
          type: boolean
        rating:
          type: number
          format: float
        review_count:
          type: integer
        related_course:
          $ref: '#/components/schemas/Course'
```

### Order Schema

```yaml
    Order:
      type: object
      properties:
        id:
          type: integer
        order_number:
          type: string
        state:
          type: string
          enum: [draft, sent, confirmed, done, cancelled]
        amount_total:
          type: number
          format: float
        currency:
          type: string
        order_line:
          type: array
          items:
            $ref: '#/components/schemas/OrderLine'
        payment_method:
          type: string
        shipping_address:
          $ref: '#/components/schemas/Address'
        created_date:
          type: string
          format: date-time
```

### Supporting Schemas

```yaml
    CourseCategory:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        description:
          type: string
    
    Instructor:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        bio:
          type: string
        photo:
          type: string
          format: uri
        expertise:
          type: string
    
    Author:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        bio:
          type: string
        photo:
          type: string
          format: uri
    
    Event:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        date_begin:
          type: string
          format: date-time
        date_end:
          type: string
          format: date-time
        location:
          type: string
    
    BlogSeries:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        description:
          type: string
        post_count:
          type: integer
    
    OrderLine:
      type: object
      properties:
        product_id:
          type: integer
        product_name:
          type: string
        quantity:
          type: integer
        price_unit:
          type: number
          format: float
        price_total:
          type: number
          format: float
    
    Address:
      type: object
      properties:
        name:
          type: string
        street:
          type: string
        city:
          type: string
        state:
          type: string
        zip:
          type: string
        country:
          type: string
        phone:
          type: string
    
    Pagination:
      type: object
      properties:
        current_page:
          type: integer
        total_pages:
          type: integer
        total_records:
          type: integer
        has_next:
          type: boolean
        has_prev:
          type: boolean
```

## Error Responses

```yaml
  Error:
    type: object
    properties:
      error:
        type: object
        properties:
          code:
            type: string
          message:
            type: string
          details:
            type: object
```

## Common Error Codes

- `AUTH_REQUIRED`: Authentication required
- `ACCESS_DENIED`: Access denied
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Input validation failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVER_ERROR`: Internal server error

## Rate Limiting

- Public endpoints: 100 requests per minute
- Authenticated endpoints: 1000 requests per minute
- Contact form: 10 submissions per hour per IP

## Versioning

API versioning follows semantic versioning:
- Major version changes indicate breaking changes
- Minor version changes add new functionality
- Patch version changes include bug fixes

Current version: v1.0.0

## Testing

All endpoints should be tested with:
- Valid input data
- Invalid input data
- Authentication scenarios
- Rate limiting
- Error handling

Test data should include Vietnamese characters and content to ensure proper encoding handling.
