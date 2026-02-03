from odoo import models, fields
import logging
import secrets
from ..services.whatsapp_api import WhatsAppService

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    # 🔐 Token seguro para descarga de factura
    whatsapp_access_token = fields.Char(
        string="WhatsApp Access Token",
        copy=False
    )

    def _generate_whatsapp_token(self):
        """Genera un token único y seguro para descarga de factura"""
        for move in self:
            if not move.whatsapp_access_token:
                move.whatsapp_access_token = secrets.token_urlsafe(32)

    def _get_whatsapp_download_url(self):
        """Genera la URL completa para descargar la factura por WhatsApp"""
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return f"{base_url}/whatsapp/invoice/{self.id}?token={self.whatsapp_access_token}"

    def action_post(self):
        # ✅ Validación normal de Odoo
        res = super().action_post()

        ICP = self.env["ir.config_parameter"].sudo()

        TOKEN = ICP.get_param("whatsapp.token")
        PHONE_NUMBER_ID = ICP.get_param("whatsapp.phone_number_id")
        TEMPLATE_NAME = ICP.get_param(
            "whatsapp.template.invoice",
            "invoice_confirmed"
        )

        for move in self:
            # Solo facturas de cliente
            if move.move_type != "out_invoice":
                continue

            # 🔐 Generar token de descarga
            move._generate_whatsapp_token()

            partner = move.partner_id

            # 📞 Obtener teléfono (SEGURO para Odoo 19)
            phone = False
            if hasattr(partner, "mobile") and partner.mobile:
                phone = partner.mobile
            elif hasattr(partner, "phone") and partner.phone:
                phone = partner.phone

            if not phone:
                _logger.warning(
                    "WhatsApp Automation: factura %s sin teléfono (%s)",
                    move.name,
                    partner.name,
                )
                continue

            # Normalizar teléfono
            phone = (
                phone.replace(" ", "")
                     .replace("-", "")
                     .replace("+", "")
            )

            # 🇦🇷 Formato E.164 Argentina
            if phone.startswith("11"):
                phone = "549" + phone
            elif phone.startswith("9"):
                phone = "54" + phone
            elif not phone.startswith("54"):
                phone = "54" + phone

            # 🔗 URL de descarga
            download_url = move._get_whatsapp_download_url()

            _logger.info(
                "WhatsApp Automation: enviando TEMPLATE %s factura %s a %s (%s)",
                TEMPLATE_NAME,
                move.name,
                partner.name,
                phone,
            )

            try:
                WhatsAppService.send_template(
                    token=TOKEN,
                    phone_number_id=PHONE_NUMBER_ID,
                    to=phone,
                    template_name=TEMPLATE_NAME,
                    lang="es_AR",
                    params=[
                        partner.name,
                        move.name,
                        download_url,
                    ],
                )

                # 📝 Registro en chatter
                move.message_post(
                    body=(
                        "📲 <b>WhatsApp enviado al cliente</b><br/>"
                        f"<b>Tel:</b> {phone}<br/>"
                        f"<b>Plantilla:</b> {TEMPLATE_NAME}<br/>"
                        f"<b>Link descarga:</b> "
                        f"<a href='{download_url}' target='_blank'>{download_url}</a>"
                    )
                )

            except Exception as e:
                _logger.error(
                    "WhatsApp Automation ERROR factura %s: %s",
                    move.name,
                    str(e),
                )

        return res
