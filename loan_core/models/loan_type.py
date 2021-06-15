# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil import relativedelta
from openerp import api, fields, models


class LoanType(models.Model):
    _name = "loan.type"
    _description = "Loan Type"

    @api.model
    def _default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(
        string="Loan Type",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    decription = fields.Text(
        string="Description",
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
        company_dependent=True,
    )
    direction = fields.Selection(
        string="Direction",
        selection=[
            ("in", "In"),
            ("out", "Out"),
        ],
        required=True,
    )
    interest_method = fields.Selection(
        string="Interest Method",
        selection=[
            ("anuity", "Anuity"),
            ("flat", "Flat"),
            ("effective", "Effective"),
        ],
        required=True,
        default="anuity",
        company_dependent=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
        default=lambda self: self._default_currency_id(),
    )
    interest_amount = fields.Float(
        string="Interest Amount",
        company_dependent=True,
    )
    maximum_loan_amount = fields.Float(
        string="Maximum Loan Amount",
        required=True,
        company_dependent=True,
    )
    maximum_installment_period = fields.Integer(
        string="Maximum Installment Period",
        company_dependent=True,
    )
    realization_journal_id = fields.Many2one(
        string="Realization Journal",
        comodel_name="account.journal",
        company_dependent=True,
        domain=[
            ("type", "=", "general"),
        ],
    )
    account_realization_id = fields.Many2one(
        string="Realization Account",
        comodel_name="account.account",
        company_dependent=True,
        domain=[
            ("type", "not in", ["view", "consolidation", "closed"]),
            ("reconcile", "=", True),
        ],
        help="Account that will server as cross-account for realization.\n\n"
        "It will use as debit account for loan in or "
        "credit account for loan out",
    )
    account_rounding_id = fields.Many2one(
        string="Rounding Account",
        comodel_name="account.account",
        company_dependent=True,
        domain=[
            ("type", "=", "other"),
        ],
    )
    interest_journal_id = fields.Many2one(
        string="Interest Journal",
        comodel_name="account.journal",
        company_dependent=True,
        domain=[
            ("type", "=", "general"),
        ],
    )
    account_interest_id = fields.Many2one(
        string="Interest Account",
        comodel_name="account.account",
        company_dependent=True,
        domain=[
            ("type", "not in", ["view", "consolidation", "closed"]),
            ("reconcile", "=", True),
        ],
    )
    account_interest_income_id = fields.Many2one(
        string="Interest Income Account",
        comodel_name="account.account",
        company_dependent=True,
        domain=[
            ("type", "=", "other"),
        ],
    )
    short_account_principle_id = fields.Many2one(
        string="Short-Term Principle Account",
        comodel_name="account.account",
        company_dependent=True,
        domain=[
            ("type", "=", "other"),
            ("reconcile", "=", True),
        ],
    )
    long_account_principle_id = fields.Many2one(
        string="Long-Term Principle Account",
        comodel_name="account.account",
        company_dependent=True,
        domain=[
            ("type", "=", "other"),
            ("reconcile", "=", True),
        ],
    )
    loan_confirm_group_ids = fields.Many2many(
        string="Allow To Confirm Loan",
        comodel_name="res.groups",
        relation="rel_loan_type_2_loan_allowed_confirm",
        column1="type_id",
        column2="group_id",
    )
    loan_cancel_group_ids = fields.Many2many(
        string="Allow To Cancel Loan",
        comodel_name="res.groups",
        relation="rel_loan_type_2_loan_allowed_cancel",
        column1="type_id",
        column2="group_id",
    )
    loan_restart_group_ids = fields.Many2many(
        string="Allow To Restart Loan",
        comodel_name="res.groups",
        relation="rel_loan_type_2_loan_allowed_restart",
        column1="type_id",
        column2="group_id",
    )
    loan_restart_approval_group_ids = fields.Many2many(
        string="Allow To Restart Approval Loan",
        comodel_name="res.groups",
        relation="rel_loan_type_2_loan_allowed_restart_approval",
        column1="type_id",
        column2="group_id",
    )

    @api.model
    def _compute_interest(
        self, loan_amount, interest, period, first_payment_date, interest_method
    ):
        if interest_method == "flat":
            return self._compute_flat(loan_amount, interest, period, first_payment_date)
        elif interest_method == "effective":
            return self._compute_effective(
                loan_amount, interest, period, first_payment_date
            )
        elif interest_method == "anuity":
            return self._compute_anuity(
                loan_amount, interest, period, first_payment_date
            )

    @api.model
    def _compute_flat(self, loan_amount, interest, period, first_payment_date):
        result = []

        principle_amount = loan_amount / period
        interest_amount = (loan_amount * (interest / 100.00)) / 12.0
        next_payment_date = datetime.strptime(first_payment_date, "%Y-%m-%d")
        for _loan_period in range(1, period + 1):
            res = {
                "schedule_date": next_payment_date.strftime("%Y-%m-%d"),
                "principle_amount": principle_amount,
                "interest_amount": interest_amount,
            }
            result.append(res)
            next_payment_date = next_payment_date + relativedelta.relativedelta(
                months=+1
            )
        return result

    @api.model
    def _compute_effective(self, loan_amount, interest, period, first_payment_date):
        result = []
        principle_amount = loan_amount / float(period)
        interest_dec = interest / 100.00
        for loan_period in range(1, period + 1):
            period_before = loan_period - 1
            interest_amount = (
                (loan_amount - (period_before * principle_amount))
                * interest_dec
                / 12.00
            )
            res = {
                "schedule_date": first_payment_date,
                "principle_amount": principle_amount,
                "interest_amount": interest_amount,
            }
            result.append(res)
        return result

    @api.model
    def _compute_anuity(self, loan_amount, interest, period, first_payment_date):
        result = []
        interest_decimal = interest / 100.00
        total_principle_amount = 0.0
        fixed_principle_amount = loan_amount * (
            (interest_decimal / 12.0)
            / (1.0 - (1.0 + (interest_decimal / 12.00)) ** -float(period))
        )
        for _loan_period in range(1, period + 1):
            interest_amount = (
                (loan_amount - total_principle_amount) * interest_decimal / 12.00
            )
            principle_amount = fixed_principle_amount - interest_amount
            res = {
                "schedule_date": first_payment_date,
                "principle_amount": principle_amount,
                "interest_amount": interest_amount,
            }
            result.append(res)
            total_principle_amount += principle_amount
        return result
