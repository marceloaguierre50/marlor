# -*- coding: utf-8 -*-
import json
import logging
import pprint

from odoo import http
from odoo.http import request
from odoo.addons.payment_mercado_pago import const
from odoo.addons.payment_mercado_pago.controllers.payment import MercadoPagoPaymentController

_logger = logging.getLogger(__name__)


class MercadoPagoPaymentControllerUX(MercadoPagoPaymentController):

    @http.route(
        f"{const.WEBHOOK_ROUTE}/<reference>",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def mercado_pago_webhook(self, reference, **kwargs):
        """Soporta:
        - Webhook JSON (body)
        - IPN/querystring: ?topic=payment&id=...
        """

        # 1) Leer JSON si vino body
        raw = request.httprequest.get_data(as_text=True) or ""
        data = {}
        if raw.strip():
            try:
                data = json.loads(raw)
            except Exception:
                _logger.warning("MP webhook: body no es JSON. raw[:200]=%r", raw[:200])

        # 2) Fallback a querystring (IPN)
        if not data:
            topic = (kwargs.get("topic") or request.params.get("topic") or "").strip().lower()
            mp_id = (kwargs.get("id") or request.params.get("id") or "").strip()
            if topic == "payment" and mp_id:
                try:
                    mp_id = int(mp_id)
                except Exception:
                    pass
                data = {"action": "payment.updated", "data": {"id": mp_id}}

        _logger.info("MP UX webhook parsed:\n%s", pprint.pformat(data))

        if data.get("action") in ("payment.created", "payment.updated"):
            payment_id = (data.get("data") or {}).get("id")
            if payment_id:
                self._verify_and_process(
                    {"external_reference": reference, "payment_id": payment_id}
                )

        return ""
