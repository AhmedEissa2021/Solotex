from odoo import models, fields, api,_

from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError



class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    location_ids = fields.Many2many(comodel_name="stock.location",string="Locations",
                                    compute='_get_locations',inverse="_inverse_locations",store=True )

    filter_location_id = fields.Many2one(comodel_name="stock.location", string="Filter Location")

    product_code = fields.Char(string="Product Code",compute='compute_product_code',
                               inverse="_inverse_product_code",store=True )


    @api.depends('product_id')
    def compute_product_code(self):
        for rec in self:
            rec.product_code=''
            if rec.product_id:
                rec.product_code=rec.product_id.default_code

    def _inverse_product_code(self):
        for rec in self:
            rec.product_code = ''
            if rec.product_id:
                rec.product_code = rec.product_id.default_code

    @api.depends('product_id')
    def _get_locations(self):
        for rec in self:
            location_list=rec.location_ids=[]
            if rec.product_id:
                stock_quant=self.env['stock.quant'].search([('product_id', '=', rec.product_id.id),('on_hand','=',True)])
                for line in stock_quant:
                    if line.location_id.usage=='internal' and line.location_id.id not in location_list:
                        location_list.append(line.location_id.id)
                rec.location_ids=location_list

    def _inverse_locations(self):
        for rec in self:
            location_list = rec.location_ids = []
            if rec.product_id:
                stock_quant = self.env['stock.quant'].search(
                    [('product_id', '=', rec.product_id.id), ('on_hand', '=', True)])
                for line in stock_quant:
                    if line.location_id.usage == 'internal' and line.location_id.id not in location_list:
                        location_list.append(line.location_id.id)
                rec.location_ids = location_list

    @api.model
    def create(self, vals):
        """ Override to handle the "inventory mode" and create a quant as
        superuser the conditions are met.
        """
        if self._is_inventory_mode() and any(
                f in vals for f in ['inventory_quantity', 'inventory_quantity_auto_apply']):
            allowed_fields = self._get_inventory_fields_create()
            allowed_fields.append('product_code')
            if any(field for field in vals.keys() if field not in allowed_fields):

                raise UserError(_("Quant's creation is restricted, you can't do this operation."))

            auto_apply = 'inventory_quantity_auto_apply' in vals
            inventory_quantity = vals.pop('inventory_quantity_auto_apply', False) or vals.pop(
                'inventory_quantity', False) or 0
            # Create an empty quant or write on a similar one.
            product = self.env['product.product'].browse(vals['product_id'])
            location = self.env['stock.location'].browse(vals['location_id'])
            lot_id = self.env['stock.production.lot'].browse(vals.get('lot_id'))
            package_id = self.env['stock.quant.package'].browse(vals.get('package_id'))
            owner_id = self.env['res.partner'].browse(vals.get('owner_id'))
            quant = self._gather(product, location, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                                 strict=True)
            if lot_id:
                quant = quant.filtered(lambda q: q.lot_id)

            if quant:
                quant = quant[0].sudo()
            else:
                quant = self.sudo().create(vals)
            if auto_apply:
                quant.write({'inventory_quantity_auto_apply': inventory_quantity})
            else:
                # Set the `inventory_quantity` field to create the necessary move.
                quant.inventory_quantity = inventory_quantity
                quant.user_id = vals.get('user_id', self.env.user.id)
                quant.inventory_date = fields.Date.today()

            return quant
        res = super(StockQuantInherit, self).create(vals)
        if self._is_inventory_mode():
            res._check_company()
        return res


class StockQuantityHistoryInherit(models.TransientModel):
    _inherit = 'stock.quantity.history'

    location_id = fields.Many2one(comodel_name="stock.location", string="Location")

    def open_at_date(self):
        action = super(StockQuantityHistoryInherit, self).open_at_date()
        active_model = self.env.context.get("active_model")
        if active_model in ["stock.valuation.layer","stock.quant"] and self.location_id:
            list_locations=[]
            stock_valuation_layer=self.env['stock.valuation.layer'].search([('location_ids', '=', self.location_id.id)])
            for line in stock_valuation_layer:
                    list_locations.append(line.id)
                    line.filter_location_id = self.location_id.id

            action["domain"].append(('id','=',list_locations))
            return action

        else:
            return action


class StockValuationLayerInherit(models.Model):
    _inherit = 'stock.valuation.layer'

    location_ids = fields.Many2many(comodel_name="stock.location",string="Locations",
                                    compute='_get_locations',inverse="_inverse_locations",store=True )

    filter_location_id = fields.Many2one(comodel_name="stock.location", string="Location")

    product_code = fields.Char(string="Product Code", compute='compute_product_code',
                               inverse="_inverse_product_code", store=True)

    @api.depends('product_id')
    def compute_product_code(self):
        for rec in self:
            rec.product_code = ''
            if rec.product_id:
                rec.product_code = rec.product_id.default_code

    def _inverse_product_code(self):
        for rec in self:
            rec.product_code = ''
            if rec.product_id:
                rec.product_code = rec.product_id.default_code

    @api.depends('product_id')
    def _get_locations(self):
        for rec in self:
            location_list=rec.location_ids=[]
            if rec.product_id:
                stock_quant=self.env['stock.quant'].search([('product_id', '=', rec.product_id.id),('on_hand','=',True)])
                for line in stock_quant:
                    if line.location_id.usage=='internal' and line.location_id.id not in location_list:
                        location_list.append(line.location_id.id)
                rec.location_ids=location_list

    def _inverse_locations(self):
        for record in self:
            for rec in self:
                location_list = rec.location_ids = []
                if rec.product_id:
                    stock_quant = self.env['stock.quant'].search(
                        [('product_id', '=', rec.product_id.id), ('on_hand', '=', True)])
                    for line in stock_quant:
                        if line.location_id.usage == 'internal' and line.location_id.id not in location_list:
                            location_list.append(line.location_id.id)
                    rec.location_ids = location_list

class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    product_code = fields.Char(string="Product Code", compute='compute_product_code',
                               inverse="_inverse_product_code", store=True)

    @api.depends('product_id')
    def compute_product_code(self):
        for rec in self:
            rec.product_code = ''
            if rec.product_id:
                rec.product_code = rec.product_id.default_code

    def _inverse_product_code(self):
        for rec in self:
            rec.product_code = ''
            if rec.product_id:
                rec.product_code = rec.product_id.default_code


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    product_code = fields.Char(string="Product Code", compute='compute_product_code',
                               inverse="_inverse_product_code", store=True)

    @api.depends('product_id')
    def compute_product_code(self):
        for rec in self:
            rec.product_code = ''
            if rec.product_id:
                rec.product_code = rec.product_id.default_code

    def _inverse_product_code(self):
        for rec in self:
            rec.product_code = ''
            if rec.product_id:
                rec.product_code = rec.product_id.default_code
