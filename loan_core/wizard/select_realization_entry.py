# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class LoanSelectRealizationEntry(models.TransientModel):
    _name = "loan.select_realization_entry"
    _description = "Select Realization Entry"

    move_line_ids = fields.Many2many(
        string="Move Lines",
        comodel_name="account.move.line",
    )

    @api.multi
    def get_loan(self):
        active_model = self.env.context.get("active_model", False)
        active_id = self.env.context.get("active_id", False)
        loan = self.env[active_model].browse([active_id])[0]
        return loan

    @api.multi
    def action_select(self):
        self.ensure_one()
        loan = self.get_loan()
        pairs = []
        move_line_header_id = loan.move_line_header_id

        if self.move_line_ids:
            pairs = move_line_header_id + self.move_line_ids
            pairs.reconcile_partial()
