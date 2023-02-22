from openerp import models, fields, api

class StockQuantityHistoryInherit(models.TransientModel):
    _inherit = 'stock.quantity.history'

    location_id = fields.Many2one(comodel_name="stock.location", string="Location")

    def open_at_date(self):
        action = super(StockQuantityHistoryInherit, self).open_at_date()
        active_model = self.env.context.get("active_model")
        if active_model == "stock.valuation.layer" and self.location_id:
            action["domain"].append(('location_ids','=',self.location_id.id))
            return action

        return action


class StockValuationLayerInherit(models.Model):
    _inherit = 'stock.valuation.layer'

    location_ids = fields.Many2many(comodel_name="stock.location",string="Locations",compute='_get_locations' )

    @api.depends('product_id')
    def _get_locations(self):
        for rec in self:
            location_list=rec.location_ids=[]
            if rec.product_id:
                stock_quant=self.env['stock.quant'].search([('product_id', '=', rec.product_id.id),('on_hand','=',True)])
                print(stock_quant,"GGGGGGGGGGGGGGGGGGGGGGG")
                for line in stock_quant:
                    print(line,"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
                    if line.location_id.id not in location_list:#and line.internal_loc==1 and line.productgroup==1:
                        location_list.append(line.location_id.id)
                rec.location_ids=location_list