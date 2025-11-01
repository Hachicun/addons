# AGENT.md

> Mục tiêu: Agent viết **module Odoo 18 tuỳ chỉnh** theo đúng chuẩn tài liệu Odoo, tận dụng OCA.

---

## 0) Kim chỉ nam

* **Ưu tiên tái sử dụng**: Khi có yêu cầu tính năng, **tìm trước trong OCA** (Odoo Community Association). Nếu có module gần tương đương → **fork/override/extend**. Nếu chưa có → scaffold module mới.

*. Luôn tạo module ở `addons/` và dùng `_inherit`, `xpath`, override method.
* **Bảo toàn upgrade**: Viết theo chuẩn, có test/cấu hình access rõ ràng để dễ nâng cấp phiên bản.
* **Tự động hoá**: Dùng script, MCP,template code để giảm thao tác thủ công.

---

## 1) Quy trình chuẩn khi nhận yêu cầu tính năng

### Bước 1 — Khảo sát OCA (bắt buộc)

Các repo phổ biến cần tra trước:

* **OCA/web**: mở rộng webclient, UX/UI.
* **OCA/server-tools**: tiện ích ORM, cron, logging, audit.
* **OCA/reporting-engine**: báo cáo QWeb/PDF, Excel.
* **OCA/connector**: tích hợp, đồng bộ dữ liệu.

**Cách tra cứu nhanh (gợi ý cho Agent):**

* Từ khoá: `<domain> + odoo + oca` (vd: "barcode odoo oca", "xlsx report oca", "audit trail oca").
* Nếu module OCA phù hợp ≥ 70%: lấy làm **base**, liệt kê khác biệt cần override.

### Bước 2 — Thiết kế

* Xác định **model**, **view**, **luồng nghiệp vụ**.
* Vẽ mapping model–table–quan hệ (ERD) cho phần mới/ảnh hưởng.
* Quy ước **tên field**: tránh đụng core; dùng prefix có nghĩa (vd: `x_`, `my_`).

### Bước 3 — Hiện thực hoá

* Nếu reuse OCA: thêm vào `depends` và mở rộng bằng `_inherit`.
* Nếu viết mới: **scaffold** module (mục 3 & 4) → điền code tối thiểu → chạy test.

### Bước 4 — Kiểm thử & kiểm tra chuẩn

* Unit test/TransactionCase cho nghiệp vụ chính.
* Kiểm tra **access** (ACL/rule), **data file** (XML/CSV), và **nâng cấp** (`-u <module>`).

### Bước 5 — Bàn giao

* Tạo CHANGELOG ngắn + hướng dẫn cài đặt/nâng cấp.

---

## 2) Tìm đúng tên bảng, trường, quan hệ (PostgreSQL + ORM)

### Công cụ bắt buộc

* **Developer Mode** trong Odoo UI: xem `Technical Name`, `Model`, `Related`.
* Proges MCP để kiểm tra các bảng, các trường, và các mối quan hệ. 
* Nếu không tự tìm ra được tên model, table, field,.. và các thứ khác hãy hướng dẫn người dùng tìm thủ công. 

---

## 3) Scaffold chuẩn của module (cấu trúc)

```
my_module/
├─ __init__.py
├─ __manifest__.py
├─ controllers/
│  ├─ __init__.py
│  └─ controllers.py
├─ models/
│  ├─ __init__.py
│  └─ models.py
├─ security/
│  └─ ir.model.access.csv
├─ views/
│  └─ views.xml
├─ data/          (tùy chọn)
├─ demo/          (tùy chọn)
└─ static/
   └─ description/ (index/icon)
```

**Ý nghĩa chính**

* `__manifest__.py`: metadata, `depends`, danh sách file data (XML/CSV) nạp khi cài.
* `models/*.py`: model & business logic. `views/*.xml`: form/tree/search/kanban/…
* `security/ir.model.access.csv`: quyền đọc/ghi/tạo/xoá.
* `controllers/*.py`: endpoint web nếu cần (mặc định file rỗng được scaffold sẵn).

---

## 4) Mẫu file quan trọng (copy-paste được)

### `__manifest__.py`

```python
{
    "name": "My Module",
    "version": "18.0.1.0.0",
    "summary": "Business feature X",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
    ],
    "installable": True,
    "application": False,
}
```

### `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,access.my.model,model_my_model,base.group_user,1,1,1,0
```

### `models/models.py`

```python
from odoo import api, fields, models

class MyModel(models.Model):
    _name = "my.model"
    _description = "My Model"

    name = fields.Char(required=True)
```

### `views/views.xml`

```xml
<odoo>
  <record id="view_my_model_tree" model="ir.ui.view">
    <field name="name">my.model.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
      <tree>
        <field name="name"/>
      </tree>
    </field>
  </record>

  <record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
      <form>
        <sheet>
          <group>
            <field name="name"/>
          </group>
        </sheet>
      </form>
    </field>
  </record>

  <menuitem id="menu_my_module_root" name="My Module"/>

  <record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form</field>
  </record>

  <menuitem id="menu_my_model"
            parent="menu_my_module_root"
            name="My Models"
            action="action_my_model"/>
</odoo>
```

---

## 5) Khi cần giao tiếp với bên ngoài qua API thì dùng 

Cài thư viện:

```bash
pip install odoorpc
```

Ví dụ script:

```python
import odoorpc

odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('mydb', 'admin', 'admin')
Partner = odoo.env['res.partner']
ids = Partner.search([('email', 'ilike', '@example.com')])
records = Partner.read(ids, ['name', 'email'])
print(records)
```

Lưu ý:

* Đặt logic tích hợp trong module riêng (vd: `my_integration`) để tách bạch nghiệp vụ lõi.
* Nếu cần public API: viết `controllers` (`type='json'`, `auth='user'|'public'`).

---

## 7) Chuẩn code & kiểm thử (checklist)

* **Manifest**: đủ metadata, `depends`, `data`. Phiên bản dùng schema `18.0.x.y.z`.
* **Model/View**: không sửa core; mở rộng bằng `_inherit` và `xpath`.
* **Access**: có `ir.model.access.csv` tối thiểu; nếu cần rule, tạo `ir.rule`.
* Không hard-code ID; dùng `xml_id`.
* **Test**: `odoo.tests.common.TransactionCase` cho nghiệp vụ quan trọng.
* **Nâng cấp**: đảm bảo `-u <module>` chạy sạch (không lỗi constraint/view/sequence).

---
## 9) Nguyên tắc đặt tên & tránh lỗi phổ biến

* **Model ↔ Table**: `res.partner` ↔ `res_partner`. Field Many2one kết thúc bằng `_id`.
* **Sản phẩm**: phân biệt `product.template` (mẫu) và `product.product` (biến thể). Tránh nhầm `product_tmpl_id` với `product_id`.
* **Không trùng field core**: thêm prefix có nghĩa để tránh đè.
* **Khai báo ****`depends`** chuẩn để module nạp đúng thứ tự.
### 10) Quy tắc đặt tên trường (field naming conventions)

* Trường (field) phải viết **chuẩn tiếng Anh** theo quy tắc snake_case (vd: `company_name`, `account_code`).
* Dùng từ vựng **chuẩn Odoo** (tham khảo core, docs, OCA) và tránh đặt tên mơ hồ/thiếu nghĩa.
* Field kết thúc bằng `_id` cho trường Many2one, `_ids` cho One2many hoặc Many2many. Ví dụ: `partner_id`, `invoice_line_ids`.
* Tránh trùng tên với trường core. Nếu mở rộng hoặc cần trường tùy chỉnh, thêm prefix có nghĩa, ví dụ: `x_`, `my_`.
* Tên field phải khai báo trong models.py và phối hợp hợp lý với các nhãn (`string=`), ghi chú (`help=`).
* Không viết tắt và không dùng tiếng Việt trong tên field.
* Tham khảo thêm quy tắc tại [Odoo Naming Conventions](https://www.odoo.com/documentation/18.0/developer/reference/addons/orm.html#fields-naming-conventions).

Ví dụ đúng:
```python
name = fields.Char(string="Name", required=True)
partner_id = fields.Many2one("res.partner", string="Partner")
invoice_line_ids = fields.One2many("account.move.line", "move_id", string="Invoice Lines")
x_custom_reference = fields.Char(string="Custom Reference")
```




---

## 11) Quy trình bắt buộc để áp dụng thay đổi Addons (Docker Compose)

Áp dụng cho repo này với dịch vụ `web` và `db`, Odoo config trong container ở `/etc/odoo/odoo.conf`, addons bind‑mount tại `/mnt/extra-addons`.

- Xác định DB đích từ file `.env` (biến `POSTGRES_DB`). Ví dụ hiện tại: `company_dev`.
- Nâng cấp module cần cập nhật (không cần restart Docker):
  - `docker compose run --rm web odoo -c /etc/odoo/odoo.conf -d company_dev -u <module_name> --stop-after-init`
  - Ví dụ cho module này: `docker compose run --rm web odoo -c /etc/odoo/odoo.conf -d company_dev -u delivery_custom --stop-after-init`
- Làm mới assets giao diện để thấy view/label mới:
  - Trình duyệt: hard refresh (Ctrl+F5) hoặc mở URL với `?debug=assets`.
  - Tùy chọn: Settings → Developer Tools → Clear Assets.
- Chỉ khi thực sự cần (hiếm): restart service web
  - `docker compose restart web`

Lưu ý khi sửa view/logic Odoo 18+
- Ưu tiên dùng `invisible="..."` thay vì `attrs` cho điều kiện đơn giản trong XML.
- Mọi field được tham chiếu trong điều kiện hiển thị phải có mặt trong view (có thể thêm dưới dạng `invisible="1"`).
- Khi sửa view/field, tăng `version` trong `__manifest__.py` để đảm bảo upgrade nạp thay đổi.


Khi cần tham khảo tài liệu thì tìm kiếm ở https://www.odoo.com/documentation/18.0/developer/tutorials.html
> **Kết luận**: Agent luôn bắt đầu bằng **khảo sát OCA**, sau đó **scaffold đúng chuẩn**, hiện thực hoá bằng **_inherit/xpath**, kiểm thử và bàn giao. không chạm core.
