# Transaction Webhook (Odoo 18 CE) — Casso Webhook V2

Short module to accept Casso Webhook V2 and create Bank Statement Lines for reconciliation in Odoo 18 CE. Focused on correctness, idempotency, and Odoo/OCA best practices.

## Features
- HTTP endpoint: `POST /casso/webhook`
- V2 only: HMAC-SHA512 signature verification
  - Header formats supported:
    - `X-Casso-Signature: t=<timestamp>,v1=<hex>` → base string is `t + "." + canonical_payload`
    - `X-Casso-Signature: sha512=<hex>` → base string is `canonical_payload`
  - `canonical_payload = json.dumps(payload, separators=(",", ":"), sort_keys=True)`
- Creates `account.bank.statement.line` under a Bank journal
- Idempotent on Casso transaction id (`data.id`) via unique field `x_tw_casso_id`
- Stores relevant Casso metadata on statement lines for traceability

## Addon
- Technical name: `transaction_webhook`
- Depends: `account`, `account_statement_base`, `account_reconcile_oca`
- Endpoint implemented in: `addons/transaction_webhook/controllers/webhook.py`

## Models & Fields
Extends `account.bank.statement.line` with:
- `x_tw_casso_id` (Char, unique): Casso `data.id`
- `x_tw_tid` (Char): bank reference from payload (`reference`)
- `x_tw_source` (Selection): currently `casso`
- `x_tw_account_identifier`, `x_tw_account_number`, `x_tw_bank_sub_acc_id`
- `x_tw_bank_abbreviation`, `x_tw_bank_name`
- `x_tw_counter_account`, `x_tw_virtual_account`

## Security
- Webhook V2 with HMAC-SHA512 signature is required. Token in URL is not used.
- Optional IP allow-list is supported.
- Strict Mode response supported (Casso expects `success: true` besides HTTP 200).

## Installation
1) Put the addon under your extra-addons path (this repo already binds to `/mnt/extra-addons`).
2) Update/Install:
```
docker compose run --rm web \
  odoo -c /etc/odoo/odoo.conf -d <DBNAME> -u transaction_webhook --stop-after-init
```

## Configuration (front-end)
Use the Odoo UI to set System Parameters (Settings → Technical → Parameters → System Parameters):

Required
- `transaction_webhook.hmac_secret`: Key bảo mật (Secret Key) từ cấu hình Webhook V2 của Casso.

Recommended
- `transaction_webhook.strict_mode`: `1` nếu bạn bật Strict Mode trong Casso; endpoint sẽ trả `{"success": true}` cùng HTTP 200.
- `transaction_webhook.default_journal_id`: ID của Bank Journal mặc định (dạng số). Sử dụng khi Odoo không suy ra được journal từ số tài khoản.

Optional
- `transaction_webhook.allowed_ips`: Danh sách IP cho phép (phân tách dấu phẩy). Để trống nếu không biết IP của Casso.
- `transaction_webhook.debug`: `1` để ghi log chẩn đoán (nên tắt sau khi ổn định).

How to find a journal ID
- Accounting → Configuration → Journals → mở Bank journal mong muốn → bật Developer Mode → xem `id` trên URL (`...model=account.journal&id=42...` → ID = 42).

## Cấu hình bên Casso
- Chọn “Webhook V2”.
- Webhook URL (HTTPS public): `https://<your-domain-or-ngrok>/casso/webhook`
- Sử dụng Key bảo mật → nhập vào Odoo (`transaction_webhook.hmac_secret`).
- (Tuỳ chọn) Strict Mode: nếu bật, Casso yêu cầu JSON trả về có `success: 1|true` ngoài HTTP 200.

## Dòng xử lý
1) Casso gọi `POST /casso/webhook` (JSON), kèm `X-Casso-Signature` V2.
2) Addon xác thực HMAC-SHA512 với secret đã cấu hình.
3) Parse `payload.data` (object V2) → dựng statement line:
   - `payment_ref`: `description` hoặc `reference` hoặc `data.id`
   - `date`: từ `transactionDateTime` (fallback today nếu thiếu/không parse được)
   - `amount`: giá trị `amount` (dương cho tiền vào; nếu cần âm cho tiền ra, mở rộng sau)
   - Gắn vào Bank journal mặc định (`transaction_webhook.default_journal_id`) hoặc tìm theo số tài khoản nếu có.
4) Idempotency: nếu đã có `x_tw_casso_id` trùng → không tạo mới; trả `created: false`.

## Test Local (curl/ngrok)
- Ngrok:
```
ngrok http 8069
# copy https public URL
```
- Cấu hình Odoo System Parameters như mục “Configuration (front-end)”.
- Gọi từ Casso (nút Gọi Thử) với URL ngrok. Hoặc gửi curl với chữ ký mẫu của Casso.

## Response Format
- Thành công: HTTP 200, JSON:
```
{"error": 0, "results": [{"casso_id": "...", "reference": "...", "line_id": 123, "created": true}], "success": true}
```
- Thất bại xác thực: HTTP 401 với `{ "error": 1, "message": "Unauthorized" }`.

## Troubleshooting
- 401 + log `Missing X-Casso-Signature` → Casso chưa gửi header signature.
- 401 + log `Signature check ... ok=False` → Sai `hmac_secret` hoặc khác công thức base (kiểm tra V2 đang bật; Casso dùng: `t + "." + JSON(sorted keys)`).
- 422 `Unsupported payload` → body không có `data` (object) theo V2.
- 500 `HMAC secret not configured` → chưa đặt `transaction_webhook.hmac_secret`.
- Không thấy line: kiểm tra Bank journal (type=bank), `transaction_webhook.default_journal_id`, và logs `docker compose logs -f web`.

## Kế toán & Odoo Best Practices
- Ghi nhận vào Bank journal (tài khoản thanh khoản 101xxx). Không post thẳng vào Receivable/Payable.
- Dùng Reconciliation (core hoặc OCA `account_reconcile_model_oca`) để đối soát với hóa đơn.

## Nâng cấp & Triển khai
- Mỗi khi sửa module, nâng version hoặc chạy upgrade:
```
docker compose run --rm web \
  odoo -c /etc/odoo/odoo.conf -d <DBNAME> -u transaction_webhook --stop-after-init
```
- Prod (Coolify/Odoo self-host): expose HTTPS domain, đặt System Parameters như dev, cập nhật Webhook URL trong Casso.

## Ghi chú phát triển
- Không còn hỗ trợ V1 (token). Chỉ V2 với HMAC-SHA512.
- Nếu cần hỗ trợ tự động xác định chiều tiền (in/out) hoặc match partner/invoice từ `description`, mở rộng tại `models/processor.py`.
- Test unit nên tập trung vào: xác thực chữ ký, idempotency, chọn journal, và tạo statement line.

