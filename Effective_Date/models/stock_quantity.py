from odoo import models, fields, api




class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    location_ids = fields.Many2many(comodel_name="stock.location",string="Locations",
                                    compute='_get_locations',inverse="_inverse_locations",store=True )

    filter_location_id = fields.Many2one(comodel_name="stock.location", string="Filter Location")

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