import json
import hmac
import hashlib
import logging
from datetime import datetime

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


def _get_param(key, default=None):
    return (
        request.env["ir.config_parameter"].sudo().get_param(key, default)
    )


class CassoWebhookController(http.Controller):
    @http.route(
        ["/casso/webhook"],
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def casso_webhook(self, **kwargs):
        debug_mode = _get_param("transaction_webhook.debug", "0") in ("1", "true", "True")
        # Webhook V2 only: no token auth, signature-based only

        # Optional IP allowlist
        allow_ips = _get_param("transaction_webhook.allowed_ips") or ""
        if allow_ips.strip():
            allowed = {ip.strip() for ip in allow_ips.split(",") if ip.strip()}
            real_ip = (
                request.httprequest.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                or request.httprequest.remote_addr
            )
            if real_ip not in allowed:
                if debug_mode:
                    _logger.info("[transaction_webhook] Forbidden IP: %s; allowed=%s", real_ip, allowed)
                return request.make_response(
                    json.dumps({"error": 1, "message": "Forbidden IP", **({"ip": real_ip} if debug_mode else {})}),
                    headers=[("Content-Type", "application/json")],
                    status=403,
                )

        # Parse JSON body
        try:
            # For type='http', prefer reading raw body to avoid relying on request.jsonrequest
            raw = request.httprequest.data or request.httprequest.get_data()
            if raw:
                payload = json.loads(raw.decode("utf-8"))
            else:
                # Fallback to attribute if present
                payload = getattr(request, "jsonrequest", None) or {}
        except Exception as e:  # noqa: BLE001
            return request.make_response(
                json.dumps({"error": 1, "message": f"Invalid JSON: {e}"}),
                headers=[("Content-Type", "application/json")],
                status=400,
            )

        # HMAC signature verification (required for V2)
        secret = _get_param("transaction_webhook.hmac_secret")
        signature = request.httprequest.headers.get("X-Casso-Signature")
        signature_ok = False
        if secret:
            raw_bytes = raw or b""
            if not signature:
                if debug_mode:
                    _logger.info("[transaction_webhook] Missing X-Casso-Signature while secret configured")
            else:
                try:
                    # Webhook V2: HMAC-SHA512 hex
                    sig_str = signature.strip()
                    provided_sig = None
                    ts = None
                    # Build canonical JSON of full payload with sorted keys (recursive)
                    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
                    if sig_str.lower().startswith("sha512="):
                        # Format: sha512=<hex>; base = canonical JSON
                        provided_sig = sig_str.split("=", 1)[1].strip()
                        base = canonical.encode("utf-8")
                    else:
                        # Format: t=<ts>,v1=<hex>; base = f"{t}.{canonical JSON}"
                        parts = dict(
                            (p.split("=", 1)[0].strip(), p.split("=", 1)[1].strip())
                            for p in sig_str.split(",") if "=" in p
                        )
                        provided_sig = parts.get("v1")
                        ts = parts.get("t")
                        base = (ts + "." + canonical).encode("utf-8") if (provided_sig and ts) else None

                    if provided_sig and base is not None:
                        digest = hmac.new(secret.encode("utf-8"), base, hashlib.sha512).hexdigest()
                        signature_ok = hmac.compare_digest(digest.lower(), provided_sig.lower())
                    if debug_mode:
                        _logger.info(
                            "[transaction_webhook] Signature check: has_ts=%s, base_len=%s, ok=%s",
                            bool(ts), len(base), signature_ok,
                        )
                except Exception:
                    if debug_mode:
                        _logger.exception("[transaction_webhook] Signature parse/verify error")

        if not signature_ok:
            payload = {"error": 1, "message": "Unauthorized"}
            if debug_mode:
                payload["reason"] = "signature_invalid_or_missing"
            return request.make_response(
                json.dumps(payload), headers=[("Content-Type", "application/json")], status=401
            )

        # Normalize to a single transaction dict (V2 uses an object in data)
        data = payload.get("data", None)
        if isinstance(data, dict):
            tx_list = [data]
        else:
            return request.make_response(
                json.dumps({"error": 1, "message": "Unsupported payload"}),
                headers=[("Content-Type", "application/json")],
                status=422,
            )

        service = request.env["transaction.webhook.service"].sudo()
        results = []
        for tx in tx_list:
            try:
                line, created = service.process_casso_payload(tx)
                results.append({
                    "casso_id": line.x_tw_casso_id,
                    "reference": line.x_tw_tid,
                    "line_id": line.id,
                    "created": bool(created),
                })
            except Exception as e:  # noqa: BLE001
                # Keep processing the rest, but report errors
                results.append({"error": 1, "message": str(e)})

        response_body = {"error": 0, "results": results}
        # For Casso Strict Mode compatibility, include success flag if enabled via param
        if _get_param("transaction_webhook.strict_mode", "0") in ("1", "true", "True"):
            response_body["success"] = True
        return request.make_response(
            json.dumps(response_body),
            headers=[("Content-Type", "application/json")],
            status=200,
        )
