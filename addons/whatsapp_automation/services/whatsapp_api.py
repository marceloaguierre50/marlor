import requests
import logging

_logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Servicio de WhatsApp Cloud API
    Compatible con:
    - Mensajes de texto (send_message)
    - Mensajes por plantilla aprobada (send_template)
    - Envío de documentos PDF (send_document)
    """

    # ---------------------------------------------------------
    # MENSAJE DE TEXTO (solo sirve con ventana 24 hs)
    # ---------------------------------------------------------
    @staticmethod
    def send_message(token, phone_number_id, to, message):
        """
        Envía un mensaje de texto simple por WhatsApp Cloud API
        (NO recomendado para producción sin ventana de 24 hs)
        """

        if not token or not phone_number_id:
            raise ValueError("Token o Phone Number ID no configurados")

        url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            },
        }

        _logger.info(
            "WhatsApp TEXT → POST %s | to=%s",
            url,
            to,
        )

        response = requests.post(url, headers=headers, json=payload, timeout=15)

        if response.status_code not in (200, 201):
            _logger.error(
                "WhatsApp TEXT ERROR %s: %s",
                response.status_code,
                response.text,
            )
            raise Exception(response.text)

        _logger.info("WhatsApp TEXT OK → mensaje enviado a %s", to)
        return True

    # ---------------------------------------------------------
    # MENSAJE POR TEMPLATE (RECOMENDADO / PRODUCCIÓN)
    # ---------------------------------------------------------
    @staticmethod
    def send_template(token, phone_number_id, to, template_name, lang, params):
        """
        Envía un mensaje usando una plantilla oficial aprobada
        """

        if not token or not phone_number_id:
            raise ValueError("Token o Phone Number ID no configurados")

        url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": lang
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": value
                            }
                            for value in params
                        ],
                    }
                ],
            },
        }

        _logger.info(
            "WhatsApp TEMPLATE → POST %s | to=%s | template=%s",
            url,
            to,
            template_name,
        )

        response = requests.post(url, headers=headers, json=payload, timeout=15)

        if response.status_code not in (200, 201):
            _logger.error(
                "WhatsApp TEMPLATE ERROR %s: %s",
                response.status_code,
                response.text,
            )
            raise Exception(response.text)

        _logger.info(
            "WhatsApp TEMPLATE OK → mensaje enviado a %s (%s)",
            to,
            template_name,
        )
        return True

    # ---------------------------------------------------------
    # ENVÍO DE DOCUMENTO (PDF)
    # ---------------------------------------------------------
    @staticmethod
    def send_document(token, phone_number_id, to, document_url, filename):
        """
        Envía un documento (PDF) por WhatsApp Cloud API
        """

        if not token or not phone_number_id:
            raise ValueError("Token o Phone Number ID no configurados")

        url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {
                "link": document_url,
                "filename": filename,
            },
        }

        _logger.info(
            "WhatsApp DOCUMENT → POST %s | to=%s | file=%s",
            url,
            to,
            filename,
        )

        response = requests.post(url, headers=headers, json=payload, timeout=20)

        if response.status_code not in (200, 201):
            _logger.error(
                "WhatsApp DOCUMENT ERROR %s: %s",
                response.status_code,
                response.text,
            )
            raise Exception(response.text)

        _logger.info("WhatsApp DOCUMENT OK → PDF enviado a %s", to)
        return True
