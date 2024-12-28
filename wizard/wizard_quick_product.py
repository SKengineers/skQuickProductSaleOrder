# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import xlrd
import os
from bs4 import BeautifulSoup


class WizardQuickProduct(models.TransientModel):
    _name = 'wizard.quick.product'
    _description = "Wizard Action Quick Product"

    select_type = fields.Selection([
        ('quick', 'Quick Import Product With quantity default = 1'),
        ('flexible', 'Quick Import Product with Custom Quantity'),
        ('file', 'Quick Import Product by file xlsx/xls'),
        ('text', 'Quick Product by Text')
    ], string='Select Type Import', default=None)

    product_ids = fields.Many2many('product.product')

    product_line_ids = fields.One2many('product.line.import', 'wizard_quick_sale_id')

    file_import = fields.Binary(string='File')
    file_name = fields.Char(string='File Name')

    text_import = fields.Text(string='Text Import')

    def import_file(self, sale_order=None):
        for this in self:
            file_type = this.file_name.split('.')[1]
            if file_type not in ['xlsx', 'xls']:
                raise UserError(_("Please input XLSX/XLS file only!"))
            try:
                recordlist = base64.decodebytes(this.file_import)
                excel = xlrd.open_workbook(file_contents=recordlist)
                sh = excel.sheet_by_index(0)

            except ValidationError:
                raise UserError(_('Please select File'))
            if sh:
                for row in range(1, sh.nrows):
                    if row > 0:
                        product_code = sh.cell(row, 0).value or False
                        if product_code:
                            product = self.env['product.product'].search([
                                ('default_code', '=', str(product_code).strip())
                            ])
                            if product:
                                value = {
                                    'product_id': product.id,
                                    'name': product.display_name,
                                    'product_uom_qty': sh.cell(row, 1).value or 0,
                                    'order_id': sale_order.id
                                }
                                self.env['sale.order.line'].create(value)

    def import_text(self, sale_order=None):
        result = []
        lines = self.text_import.strip().splitlines()
        for line in lines:
            if line:
                if line.count(',') != 1:
                    raise UserError(_(f"Invalid format: Line '{line}' does not have exactly one comma."))
                parts = line.split(',')
                if len(parts) != 2:
                    raise UserError(_(f"Invalid format: Line '{line}' has more than one comma."))
                if len(parts) == 2:
                    code, quantity = parts
                    if not quantity.strip().isdigit():
                        raise UserError(_(f"Invalid format: Quantity '{quantity}' in line '{line}' is not a number."))
                    result.append({
                        'default_code': code.strip(),
                        'quantity': int(quantity.strip())
                    })
        for pro in result:
            product = self.env['product.product'].search([
                ('default_code', '=', pro['default_code'].strip())
            ])
            if not product:
                raise UserError(_("Product cannot found %s" % pro['default_code']))
            value = {
                'product_id': product.id,
                'name': product.display_name,
                'product_uom_qty': pro['quantity'],
                'order_id': sale_order.id
            }
            self.env['sale.order.line'].create(value)

    def action_import(self):
        sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        if self.select_type == 'quick':
            for pro in self.product_ids:
                value = {
                    'product_id': pro.id,
                    'name': pro.display_name,
                    'product_uom_qty': 1,
                    'order_id': sale_order.id
                }
                self.env['sale.order.line'].create(value)
        if self.select_type == 'flexible':
            for pro in self.product_line_ids:
                value = {
                    'product_id': pro.product_id.id,
                    'name': pro.product_id.display_name,
                    'product_uom_qty': pro.quantity,
                    'order_id': sale_order.id
                }
                self.env['sale.order.line'].create(value)
        if self.select_type == 'file':
            self.import_file(sale_order=sale_order)
        if self.select_type == 'text':
            self.import_text(sale_order=sale_order)


class ProductLineImport(models.TransientModel):
    _name = 'product.line.import'

    wizard_quick_sale_id = fields.Many2one('wizard.quick.product')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Integer(string='Quantity')