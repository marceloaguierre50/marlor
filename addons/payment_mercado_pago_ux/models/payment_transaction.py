from odoo import models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _mercado_pago_prepare_preference_request_payload(self):
        payload = super()._mercado_pago_prepare_preference_request_payload()

        # Quitar cuotas si existen
        if 'payment_methods' in payload and 'installments' in payload['payment_methods']:
            del payload['payment_methods']['installments']

        # Definir explícitamente las URLs de retorno (OBLIGATORIO en test y prod)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        payload['back_urls'] = {
            'success': base_url + '/shop/payment/validate',
            'failure': base_url + '/shop/payment/validate',
            'pending': base_url + '/shop/payment/validate',
        }

        payload['auto_return'] = 'approved'

        return payload
