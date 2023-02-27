# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.exceptions import ValidationError
from datetime import datetime,date

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	real_date = fields.Datetime(string="Effective Date" )


class StockMove(models.Model):
	_inherit = 'stock.move'

	def _action_done(self,cancel_backorder=True):
		real_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
		for move in self:
			if move.picking_id:
				if move.picking_id.real_date:
					real_date = move.picking_id.real_date
				else:
					raise ValidationError(_('effective Date can not be empty .'))

					# real_date = move.picking_id.scheduled_date
			
		res = super(StockMove, self)._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
		if real_date:
			for move in res:
				move.write({'date':real_date})
				if move.move_line_ids:
					for move_line in move.move_line_ids:
						move_line.write({'date':real_date})
		else: raise ValidationError(_('effective Date can not be empty .'))

				
		return res


	def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
		self.ensure_one()
		AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

		print("aaaaaa",AccountMove)
		for rec in self:
				print("xxxxxxxxxx",rec['date'])



		move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
		if move_lines:
			# mrp = self.env['mrp.production'].sudo().search_read()



			# print("move_lines",move_lines[2]['name'].split(" ,")[0])
			date = self._context.get('force_period_date', fields.Date.context_today(self))
			for x in move_lines:

				s=x[2]['name'].split(" ")[0]
				# print(x[2]['name'].split(" ")[0],"ssssss")
				mrp = self.env['mrp.production'].sudo().search_read([('name',"=",s)])

				for r in mrp:
					date = datetime.strptime(str(r['date_planned_start']).split(".")[0], '%Y-%m-%d %H:%M:%S').date()

			if self.picking_id.real_date:
				date = self.picking_id.real_date.date()

			new_account_move = AccountMove.sudo().create({
				'journal_id': journal_id,
				'line_ids': move_lines,
				'date': date,
				'ref': description,
				'stock_move_id': self.id,
				'stock_valuation_layer_ids': [(6, None, [svl_id])],
				'move_type': 'entry',
			})
			new_account_move._post()
