# Feature Specification: Lục Khí Website Platform

**Feature Branch**: `001-website`  
**Created**: 2025-10-29  
**Status**: Draft  
**Input**: User description: "Context

Lục Khí là hệ thống tri thức và phương pháp thực hành giúp con người tự hiểu, tự điều chỉnh sức khỏe theo nguyên lý Đông Y hiện đại hóa.

Hiện tại, doanh nghiệp có website cơ bản, muốn chuyển toàn bộ sang Odoo CE 18 để quản lý thống nhất: nội dung, khóa học, khách hàng, bán hàng và cộng đồng.

Hệ thống được xây dựng bằng custom module, không dùng kéo-thả, để đảm bảo khả năng mở rộng, bảo trì và tích hợp sâu với CRM, eLearning, eCommerce.

Goals / Why

Xây dựng website chính thức Lục Khí – nền tảng truyền thông, đào tạo và kinh doanh.

Quản lý nội dung và học viên chuyên nghiệp, dễ mở rộng về sau.

Tận dụng các module chính thức của Odoo CE & OCA để rút ngắn thời gian phát triển.

Dễ dàng nâng cấp lên nền tảng số toàn diện (Odoo ERP + Website + eLearning + CRM).

Giá trị mang lại:

Tập trung toàn bộ hoạt động kinh doanh và đào tạo về một nơi.

Tăng uy tín thương hiệu thông qua giao diện và trải nghiệm chuyên nghiệp.

Giảm chi phí quản lý và phát triển lâu dài.

Users & Use Cases

1. Khách truy cập (Public User)

Truy cập website, xem giới thiệu, khóa học, bài viết, sản phẩm.

Đăng ký nhận tư vấn hoặc đăng ký tham gia cộng đồng (form).

Đặt hàng (mua sách, dịch vụ).

2. Học viên đã đăng ký

Đăng nhập và truy cập khu vực học online.

Xem video, tải tài liệu, làm bài kiểm tra (slides/quiz).

Theo dõi tiến độ học tập.

3. Quản trị viên / Nhân viên nội bộ

Quản lý bài viết (blog).

Quản lý khóa học, học viên, và phân quyền truy cập.

Quản lý sản phẩm, dịch vụ, đơn hàng.

Nhận và xử lý form liên hệ / tư vấn từ CRM.

Scope / What

1. Trang chính & điều hướng

Trang chủ (giới thiệu tổng quan, khóa học nổi bật, bài viết mới nhất).

Menu chính:

Giới thiệu (About Lục Khí, tầm nhìn – sứ mệnh – đội ngũ).

Khóa học (Danh sách khóa học: Lục Khí Cơ Bản, Trung Cấp 1–3).

Blog (bài viết, chuyên mục, tags).

Sản phẩm – Dịch vụ (sách, khám bệnh, dịch vụ).

Cộng đồng (CLB, nhóm Zalo).

Liên hệ (form gửi lead CRM).

2. Chức năng chi tiết

Khóa học

Hiển thị danh sách khóa học.

Mỗi khóa học có: tên, cấp độ, mô tả, hình ảnh, giá, link video học.

Khi học viên đăng nhập → thấy khóa học của mình (e-learning).

Tích hợp website_slides để hiển thị video, tài liệu, quiz.

Blog

Dùng website_blog.

Phân loại chuyên mục (kiến thức, lối sống, cộng đồng…).

Giao diện hiển thị bài viết mới nhất, bài nổi bật.

Sản phẩm – Dịch vụ

Dùng website_sale.

Hiển thị sản phẩm (sách, dịch vụ khám, khóa học có thể mua).

Giỏ hàng và đặt hàng cơ bản (COD hoặc chuyển khoản).


Liên hệ / CRM

Form liên hệ (tư vấn, đăng ký học thử).

Dùng website_form và tự động tạo lead trong CRM.

Trang giới thiệu (About Page)

"Lục Khí là gì?", "Tầm nhìn – Sứ mệnh – Giá trị cốt lõi".

Giới thiệu đội ngũ giảng viên, cộng sự.

SEO & Analytics

Dùng website_seo và website_google_analytics.

Cấu hình chuẩn SEO cho từng trang (title, meta, open graph).

Constraints

Dùng Odoo CE 18 (Community Edition).

Không sử dụng module kéo-thả (website_editor chỉ bật cho chỉnh sửa nhỏ).

Ưu tiên module chính thức Odoo + OCA (không code lại trùng chức năng).

Triển khai bằng Python 3.11, PostgreSQL 16.

Code theo chuẩn Odoo ORM, MVC, QWeb.

Ngôn ngữ giao diện: Tiếng Việt, có thể mở rộng i18n.

Acceptance Criteria

Mục tiêu	Tiêu chí chấp nhận (testable)

Trang chủ hiển thị đúng	Truy cập / hiển thị banner, khóa học, blog mới nhất

Menu hoạt động	Toàn bộ menu chính hoạt động, load nội dung tương ứng

Blog	Có thể tạo bài viết mới, hiển thị theo chuyên mục

Khóa học	Người dùng đăng nhập có thể xem nội dung khóa học (video, tài liệu)

E-learning	Học viên chỉ thấy khóa học đã mua hoặc được gán

Sản phẩm	Có thể đặt hàng sách hoặc dịch vụ, tạo đơn bán hàng

Form liên hệ	Gửi form → lead xuất hiện trong CRM


Giao diện responsive	Hiển thị tốt trên mobile và desktop

SEO	Có meta tag, sitemap, Google Analytics hoạt động"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Public Website Browsing (Priority: P1)

Khách truy cập có thể truy cập website, xem thông tin giới thiệu, danh sách khóa học, bài viết blog và sản phẩm một cách dễ dàng trên cả desktop và mobile.

**Why this priority**: Đây là nền tảng cơ bản nhất - không có chức năng này thì không có website. Khách hàng cần có thể khám phá nội dung trước khi quyết định đăng ký hoặc mua hàng.

**Independent Test**: Có thể test bằng cách truy cập trang chủ và điều hướng qua tất cả các menu chính mà không cần đăng nhập. Mỗi trang phải hiển thị nội dung phù hợp và responsive trên mobile.

**Acceptance Scenarios**:

1. **Given** khách truy cập chưa đăng nhập, **When** truy cập trang chủ, **Then** hiển thị banner giới thiệu, khóa học nổi bật, và bài viết mới nhất
2. **Given** khách truy cập đang xem trang chủ, **When** click vào menu "Khóa học", **Then** hiển thị danh sách tất cả khóa học với thông tin cơ bản
3. **Given** khách truy cập đang dùng mobile, **When** truy cập bất kỳ trang nào, **Then** giao diện hiển thị đúng và dễ sử dụng trên màn hình nhỏ

---

### User Story 2 - Course Enrollment and Learning (Priority: P1)

Học viên có thể đăng ký, mua khóa học và truy cập khu vực học tập để xem video, tải tài liệu và làm bài kiểm tra.

**Why this priority**: Đây là chức năng cốt lõi tạo ra doanh thu và giá trị chính cho Lục Khí. Không có chức năng này thì không thể bán và cung cấp khóa học.

**Independent Test**: Có thể test đầy đủ từ quy trình mua khóa học đến truy cập nội dung học tập. Học viên chỉ thấy các khóa học đã đăng ký và có thể hoàn thành các hoạt động học tập cơ bản.

**Acceptance Scenarios**:

1. **Given** người dùng chưa đăng nhập, **When** chọn khóa học và nhấn "Đăng ký", **Then** được hướng dẫn đến trang đăng ký/đăng nhập
2. **Given** học viên đã đăng nhập và đã mua khóa học, **When** vào trang khóa học, **Then** thấy video học, tài liệu và quiz
3. **Given** học viên đang học, **When** hoàn thành một bài học, **Then** tiến độ học tập được cập nhật

---

### User Story 3 - Content Management (Priority: P2)

Quản trị viên có thể tạo và quản lý bài viết blog, khóa học, và sản phẩm thông qua giao diện quản trị của Odoo.

**Why this priority**: Cần thiết để duy trì nội dung mới và thu hút người dùng. Tuy nhiên có thể bắt đầu với nội dung ban đầu và thêm sau.

**Independent Test**: Có thể test bằng cách đăng nhập với quyền admin và tạo mới/cập nhật/xóa từng loại nội dung. Mọi thay đổi phải hiển thị đúng trên website public.

**Acceptance Scenarios**:

1. **Given** admin đăng nhập vào backend, **When** tạo bài viết blog mới, **Then** bài viết xuất hiện trên trang blog với đúng chuyên mục
2. **Given** admin đăng nhập vào backend, **When** tạo khóa học mới, **Then** khóa học xuất hiện trong danh sách và có thể mua
