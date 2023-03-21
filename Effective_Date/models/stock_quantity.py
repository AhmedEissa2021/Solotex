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


    def _apply_inventory(self):
        move_vals = []
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(_('Only a stock manager can validate an inventory adjustment.'))
        for quant in self:
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if float_compare(quant.inventory_diff_quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0:
                move_vals.append(
                    quant._get_inventory_move_values(quant.inventory_diff_quantity,
                                                     quant.product_id.with_company(quant.company_id).property_stock_inventory,
                                                     quant.location_id))
            else:
                move_vals.append(
                    quant._get_inventory_move_values(-quant.inventory_diff_quantity,
                                                     quant.location_id,
                                                     quant.product_id.with_company(quant.company_id).property_stock_inventory,
                                                     out=True))
        moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
        moves._action_done()
        self.location_id.write({'last_inventory_date': fields.Date.today()})
        date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
        for quant in self:
            quant.inventory_date = date_by_location[quant.location_id]
        self.write({'inventory_quantity': 0, 'user_id': False})
        self.write({'inventory_diff_quantity': 0})
        if moves and moves.move_line_ids and self.accounting_date:
            for line in moves.move_line_ids:
                if line.date:
                    line.date=self.accounting_date




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
