# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class LoanSelectRealizationEntryOut(models.TransientModel):
    _name = "loan.select_realization_entry_out"
    _description = "Select Realization Entry Out"
    _inherit = ["loan.select_realization_entry"]

    @api.model
    def _default_loan_id(self):
        active_id = self.env.context.get("active_id", False)
        return active_id

    loan_id = fields.Many2one(
        string="Loan",
        comodel_name="loan.out",
        default=lambda self: self._default_loan_id(),
    )

    allowed_move_line_ids = fields.Many2many(
        string="Allowed Move Lines",
        comodel_name="account.move.line",
        related="loan_id.allowed_move_line_ids",
        store=False,
    )
