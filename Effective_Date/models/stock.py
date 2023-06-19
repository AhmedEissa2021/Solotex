# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from collections import defaultdict
from odoo.exceptions import ValidationError
from datetime import datetime,date
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import clean_context, OrderedSet
from odoo.exceptions import UserError


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	real_date = fields.Datetime(string="Effective Date" )

	def _action_done(self):
		"""Call `_action_done` on the `stock.move` of the `stock.picking` in `self`.
        This method makes sure every `stock.move.line` is linked to a `stock.move` by either
        linking them to an existing one or a newly created one.

        If the context key `cancel_backorder` is present, backorders won't be created.

        :return: True
        :rtype: bool
        """
		self._check_company()

		todo_moves = self.mapped('move_lines').filtered(
			lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
		for picking in self:
			if picking.owner_id:
				picking.move_lines.write({'restrict_partner_id': picking.owner_id.id})
				picking.move_line_ids.write({'owner_id': picking.owner_id.id})
		todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
		self.write({'date_done': self.real_date, 'priority': '0'})

		# if incoming moves make other confirmed/partially_available moves available, assign them
		done_incoming_moves = self.filtered(lambda p: p.picking_type_id.code == 'incoming').move_lines.filtered(
			lambda m: m.state == 'done')
		done_incoming_moves._trigger_assign()

		self._send_confirmation_email()
		return True


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


		res = super(StockMove, self)._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))

		if real_date:

			for move in res:
				move.write({'date':real_date})
				if move.move_line_ids:
					for move_line in move.move_line_ids:
						move_line.write({'date':real_date})
				if move.stock_valuation_layer_ids:
					for stock_value in move.stock_valuation_layer_ids:
						if stock_value.account_move_id:
							stock_value.account_move_id.date=real_date
		else: raise ValidationError(_('effective Date can not be empty .'))


		return res


	def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
		self.ensure_one()
		AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)
		move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
		if move_lines:
			date = self._context.get('force_period_date', fields.Date.context_today(self))
			for x in move_lines:

				s=x[2]['name'].split(" ")[0]

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
