from odoo import _, fields, models

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_payment_method_codes = super()._get_default_payment_method_codes()
        if self.code != 'mercado_pago':
            return default_payment_method_codes
        const = [pm for pm in default_payment_method_codes if pm != 'card']
        const.insert(0, 'mercado_pago')
        return const
