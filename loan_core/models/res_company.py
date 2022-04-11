# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    cron_loan_in_interest_realization_id = fields.Many2one(
        string="Loan In Interest Realization Cron",
        comodel_name="ir.cron",
    )

    cron_loan_out_interest_realization_id = fields.Many2one(
        string="Loan Out Interest Realization Cron",
        comodel_name="ir.cron",
    )
