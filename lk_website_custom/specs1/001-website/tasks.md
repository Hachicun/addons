---

description: "Task list for Lục Khí Website Platform implementation - Module Development Focus"

---

# Tasks: Lục Khí Website Platform

**Input**: Design documents from `/specs/001-website/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md

**Focus**: Module development only - No performance, deployment, or payment gateway tasks

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Odoo Multi-module**: `luc_khi_website/`, `luc_khi_courses/`, `luc_khi_blog/`, `luc_khi_shop/`, `luc_khi_crm/`
- **Paths shown below assume Odoo module structure**

## Phase 1: Module Structure Setup

**Purpose**: Create basic Odoo module structure

- [X] T001 Create luc_khi_website module directory structure
- [X] T002 Create luc_khi_courses module directory structure
- [X] T003 Create luc_khi_blog module directory structure
- [X] T004 Create luc_khi_shop module directory structure
- [X] T005 Create luc_khi_crm module directory structure

---

## Phase 2: User Story 1 - Public Website Browsing (Priority: P1) 🎯 MVP

**Goal**: Enable public users to browse website, view information, courses, blog, and products

**Independent Test**: Access homepage, navigate all menus, verify responsive design on mobile without login

### Implementation for User Story 1

- [X] T006 [P] [US1] Create luc_khi_website module manifest in luc_khi_website/__manifest__.py
- [X] T007 [P] [US1] Create luc_khi_website.page model in luc_khi_website/models/luc_khi_website_page.py
- [X] T008 [P] [US1] Create luc_khi_website.team.member model in luc_khi_website/models/luc_khi_team_member.py
- [X] T009 [P] [US1] Create homepage controller in luc_khi_website/controllers/main.py
- [X] T010 [P] [US1] Create about page controller in luc_khi_website/controllers/main.py
- [X] T011 [P] [US1] Create contact page controller in luc_khi_website/controllers/main.py
- [X] T012 [P] [US1] Create homepage template in luc_khi_website/views/templates.xml
- [X] T013 [P] [US1] Create about page template in luc_khi_website/views/templates.xml
- [X] T014 [P] [US1] Create contact page template in luc_khi_website/views/templates.xml
- [X] T015 [P] [US1] Create website page views in luc_khi_website/views/luc_khi_website_page_views.xml
- [X] T016 [P] [US1] Create team member views in luc_khi_website/views/luc_khi_team_member_views.xml
- [X] T017 [P] [US1] Create menu structure in luc_khi_website/views/menus.xml
- [X] T018 [US1] Add Vietnamese language support in luc_khi_website/i18n/vi.po
- [X] T019 [US1] Create module data in luc_khi_website/data/website_data.xml

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 3: User Story 2 - Course Enrollment and Learning (Priority: P1)

**Goal**: Enable students to register, purchase courses, and access learning content

**Independent Test**: Complete full workflow from course discovery to accessing purchased course content

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create luc_khi_courses module manifest in luc_khi_courses/__manifest__.py
- [ ] T021 [P] [US2] Create luc_khi.course model in luc_khi_courses/models/luc_khi_course.py
- [ ] T022 [P] [US2] Create luc_khi.course.category model in luc_khi_courses/models/luc_khi_course_category.py
- [ ] T023 [P] [US2] Create luc_khi.course.tag model in luc_khi_courses/models/luc_khi_course_tag.py
- [ ] T024 [P] [US2] Create course controller in luc_khi_courses/controllers/main.py
- [ ] T025 [P] [US2] Create course list template in luc_khi_courses/views/templates.xml
- [ ] T026 [P] [US2] Create course detail template in luc_khi_courses/views/templates.xml
- [ ] T027 [P] [US2] Create my-courses portal template in luc_khi_courses/views/templates.xml
- [ ] T028 [P] [US2] Create course views in luc_khi_courses/views/luc_khi_course_views.xml
- [ ] T029 [US2] Implement Vietnamese slug generation in luc_khi_courses/models/luc_khi_course.py
- [ ] T030 [US2] Integrate with website_slides for course content in luc_khi_courses/models/luc_khi_course.py
- [ ] T031 [US2] Implement course access control in luc_khi_courses/controllers/main.py
- [ ] T032 [US2] Add Vietnamese language support in luc_khi_courses/i18n/vi.po
- [ ] T033 [US2] Create course data in luc_khi_courses/data/course_data.xml

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 4: User Story 3 - Content Management (Priority: P2)

**Goal**: Enable administrators to create and manage blog posts, courses, products, and events

**Independent Test**: Admin can create/edit/delete all content types and see changes reflected on public site

### Implementation for User Story 3

- [ ] T034 [P] [US3] Create luc_khi_blog module manifest in luc_khi_blog/__manifest__.py
- [ ] T035 [P] [US3] Extend blog.post model in luc_khi_blog/models/blog_post.py
- [ ] T036 [P] [US3] Create blog.series model in luc_khi_blog/models/blog_series.py
- [ ] T037 [P] [US3] Create blog controller in luc_khi_blog/controllers/main.py
- [ ] T038 [P] [US3] Create blog list template in luc_khi_blog/views/templates.xml
- [ ] T039 [P] [US3] Create blog detail template in luc_khi_blog/views/templates.xml
- [ ] T040 [P] [US3] Create blog views in luc_khi_blog/views/blog_post_views.xml
- [ ] T041 [US3] Implement Vietnamese blog categories in luc_khi_blog/models/blog_post.py
- [ ] T042 [US3] Add blog SEO optimization in luc_khi_blog/models/blog_post.py
- [ ] T043 [US3] Create blog management views in luc_khi_blog/views/blog_post_views.xml
- [ ] T044 [US3] Add Vietnamese language support in luc_khi_blog/i18n/vi.po
- [ ] T045 [US3] Implement blog-course cross-linking in luc_khi_blog/models/blog_post.py

**Checkpoint**: User Story 3 should now be independently functional

---

## Phase 5: User Story 4 - E-commerce and Sales (Priority: P2)

**Goal**: Enable customers to browse products, add to cart, and complete purchases

**Independent Test**: Complete full e-commerce workflow from product discovery to order completion

### Implementation for User Story 4

- [ ] T046 [P] [US4] Create luc_khi_shop module manifest in luc_khi_shop/__manifest__.py
- [ ] T047 [P] [US4] Extend product.template model in luc_khi_shop/models/product_template.py
- [ ] T048 [P] [US4] Create shop controller in luc_khi_shop/controllers/main.py
- [ ] T049 [P] [US4] Create product list template in luc_khi_shop/views/templates.xml
- [ ] T050 [P] [US4] Create product detail template in luc_khi_shop/views/templates.xml
- [ ] T051 [P] [US4] Create product views in luc_khi_shop/views/product_template_views.xml
- [ ] T052 [US4] Implement Vietnamese product types in luc_khi_shop/models/product_template.py
- [ ] T053 [US4] Add VND currency formatting in luc_khi_shop/models/product_template.py
- [ ] T054 [US4] Implement course-product auto-access in luc_khi_shop/models/product_template.py
- [ ] T055 [US4] Create Vietnamese compliance fields in luc_khi_shop/models/product_template.py
- [ ] T056 [US4] Add Vietnamese language support in luc_khi_shop/i18n/vi.po
- [ ] T057 [US4] Create product data in luc_khi_shop/data/product_data.xml

**Checkpoint**: User Story 4 should now be independently functional

---

## Phase 6: User Story 5 - Contact and Lead Generation (Priority: P3)

**Goal**: Enable visitors to submit contact forms and automatically create CRM leads

**Independent Test**: Form submission creates lead in CRM with correct information and sends confirmation

### Implementation for User Story 5

- [ ] T058 [P] [US5] Create luc_khi_crm module manifest in luc_khi_crm/__manifest__.py
- [ ] T059 [P] [US5] Extend crm.lead model in luc_khi_crm/models/crm_lead.py
- [ ] T060 [P] [US5] Create contact controller in luc_khi_crm/controllers/main.py
- [ ] T061 [P] [US5] Create contact form template in luc_khi_crm/views/templates.xml
- [ ] T062 [P] [US5] Create CRM views in luc_khi_crm/views/crm_lead_views.xml
- [ ] T063 [US5] Implement Vietnamese lead categorization in luc_khi_crm/models/crm_lead.py
- [ ] T064 [US5] Add Zalo phone field in luc_khi_crm/models/crm_lead.py
- [ ] T065 [US5] Implement lead-course interest tracking in luc_khi_crm/models/crm_lead.py
- [ ] T066 [US5] Create automated follow-up scheduling in luc_khi_crm/models/crm_lead.py
- [ ] T067 [US5] Add Vietnamese language support in luc_khi_crm/i18n/vi.po
- [ ] T068 [US5] Setup email templates for Vietnamese market in luc_khi_crm/data/email_data.xml

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Module Integration & Polish

**Purpose**: Final integration and basic polish across all modules

- [ ] T069 [P] Create module dependencies and installation order
- [ ] T070 [P] Add Vietnamese language files across all modules
- [ ] T071 [P] Create basic CSS for Vietnamese typography
- [ ] T072 [P] Implement basic responsive design
- [ ] T073 [P] Add basic SEO meta tags across all modules
- [ ] T074 [P] Create module security groups and access rights
- [ ] T075 [P] Add basic error handling and validation
- [ ] T076 [P] Create module documentation and README files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Module Structure (Phase 1)**: No dependencies - can start immediately
- **User Stories (Phase 2-6)**: Can proceed in parallel after module structure
- **Integration (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 1 - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Phase 1 - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Phase 1 - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P2)**: Can start after Phase 1 - May integrate with US2 for course sales
- **User Story 5 (P3)**: Can start after Phase 1 - May integrate with all stories for lead generation

### Within Each User Story

- Models before controllers and views
- Controllers before templates
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All module structure tasks marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Controllers within a story marked [P] can run in parallel
- Templates within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Create luc_khi_website.page model in luc_khi_website/models/luc_khi_website_page.py"
Task: "Create luc_khi_website.team.member model in luc_khi_website/models/luc_khi_team_member.py"

# Launch all controllers for User Story 1 together:
Task: "Create homepage controller in luc_khi_website/controllers/main.py"
Task: "Create about page controller in luc_khi_website/controllers/main.py"
Task: "Create contact page controller in luc_khi_website/controllers/main.py"

# Launch all templates for User Story 1 together:
Task: "Create homepage template in luc_khi_website/views/templates.xml"
Task: "Create about page template in luc_khi_website/views/templates.xml"
Task: "Create contact page template in luc_khi_website/views/templates.xml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Module Structure
2. Complete Phase 2: User Story 1
3. **STOP and VALIDATE**: Test User Story 1 independently
4. Deploy/demo if ready

### Incremental Delivery

1. Complete Module Structure → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Module Structure together
2. Once Module Structure is done:
   - Developer A: User Story 1 (luc_khi_website)
   - Developer B: User Story 2 (luc_khi_courses)
   - Developer C: User Story 3 (luc_khi_blog)
   - Developer D: User Story 4 (luc_khi_shop)
   - Developer E: User Story 5 (luc_khi_crm)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Focus on Vietnamese language support and basic functionality
- Stop at any checkpoint to validate story independently
- Avoid: performance optimization, deployment scripts, payment gateway integration
- Total tasks: 76 (5 structure + 61 user story + 10 integration)
- Tasks per user story: US1(14), US2(14), US3(12), US4(12), US5(11)
- Parallel opportunities: 61 tasks marked [P] for parallel execution
