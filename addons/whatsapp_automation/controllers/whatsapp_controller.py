from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WhatsAppInvoiceController(http.Controller):

    @http.route(
        "/whatsapp/invoice/<int:move_id>",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False
    )
    def whatsapp_invoice_pdf(self, move_id, token=None, **kwargs):
        try:
            move = request.env["account.move"].sudo().browse(move_id)

            # Validaciones básicas
            if not move.exists():
                return request.not_found()

            if move.move_type != "out_invoice":
                return request.not_found()

            # Validar token
            if not token or token != move.whatsapp_access_token:
                return request.not_found()

            # ✅ REPORTE FACTURA ODOO 19 (FORMA CORRECTA)
            report = request.env["ir.actions.report"].sudo()._get_report_from_name(
                "account.report_invoice"
            )

            pdf_content, _ = report.with_context(
                active_model="account.move",
                active_ids=[move.id],
            ).render_qweb_pdf([move.id])

            filename = f"{move.name}.pdf"

            headers = [
                ("Content-Type", "application/pdf"),
                (
                    "Content-Disposition",
                    f'attachment; filename="{filename}"',
                ),
            ]

            return request.make_response(pdf_content, headers=headers)

        except Exception:
            _logger.exception(
                "WhatsApp Invoice Download ERROR move_id=%s", move_id
            )
            return request.not_found()
