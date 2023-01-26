# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, _, tools
_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def amount_to_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        if num2words is None:
            logging.getLogger(__name__).warning(
                "The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        formatted = "%.{0}f".format(self.currency_id.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang_code = self.env.user.lang or self.env.context.get('lang')
        lang = self.env['res.lang'].with_context(active_test=False).search([('code', '=', lang_code)])
        if self.currency_id.name == 'USD':
            value_unit = 'USD'
        else:
            value_unit = 'M.N'
        amount_words = tools.ustr(_('{amt_value} {amt_word} {amt_decimal}/100 {amt_value_unit}')).format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_decimal=fractional_value,
            amt_word=self.currency_id.currency_unit_label,
            amt_value_unit=value_unit,
        )
        amount_words = amount_words.upper()
        if lang_code == 'es_MX':
            amount_words = amount_words.replace('DOLLARS', 'DOLARES')
        return amount_words.replace(" 0/", " 00/")