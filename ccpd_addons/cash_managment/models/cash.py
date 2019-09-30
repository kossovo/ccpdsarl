# !/usr/bin/env python
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CashLine(models.Model):
    """
    Line of cash register
    """
    _name = 'cash.line'

    name = fields.Char('Description', required=True)
    date = fields.Date(string='Date', required=True, help='Date de la dépense')
    reference = fields.Char(
        string='Référence', size=64, help='Référence')
    invoice_id = fields.Many2one(
        'account.invoice', string='Facture lié',
        help='Facture fournisseur ou client liée à cette dépenses')
    partner_id = fields.Many2one(
        'res.partner', string='Partenaire', help='Partenaire lié')
    amount = fields.Integer(
        string='Montant', help='Montant de la dépense')
    cash_id = fields.Many2one(
        'cash.register', string='Caisse',
        help='Caisse liée à cette ligne de dépense')
    sequence = fields.Integer(
        string='Sequence', index=True,
        help='Gives the sequence order when displaying a list of bank statement lines')


class Cash(models.Model):
    """
    Manage cash flow
    """
    _name = 'cash.register'
    _description = "Cash"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _compute_default_cash_name(self, journal_id):
        return self.env['ir.sequence'].next_by_id(
            journal_id.sequence_id.id)

    def _default_journal_id(self):
        journal_ids = self.env['account.journal'].search([
            ('type', '=', 'cash')])
        # Les dépenses sont faite en CFA
        for journal in journal_ids:
            if journal.currency == self._default_currency:
                return journal
        return False

    def _default_currency(self):
        """ return the default currency """
        return self.env['res.users'].browse(self._uid).company_id.currency_id

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            journal_id = vals.get(
                'journal_id', self._default_journal_id())
            vals['name'] = self._compute_default_cash_name(journal_id)
        if 'line_ids' in vals:
            for idx, line in enumerate(vals['line_ids']):
                line[2]['sequence'] = idx + 1
        return super(Cash, self).create(vals)

    @api.multi
    def _end_balance(self):
        res = {}
        for statement in self:
            res[self.id] = self.balance_start
            for line in self.line_ids:
                res[self.id] += line.amount
        return res

    name = fields.Char(
        string='Référence', size=64, help='Référence de la caisse',
        default='/', readonly=True, copy=False)
    date = fields.Date(
        'Date', required=True, states={'confirm': [('readonly', True)]},
        index=True, copy=False, default=fields.Date.context_today)
    journal_id = fields.Many2one(
        'account.journal', 'Journal', required=True,
        default=lambda self: self._default_journal_id(),
        readonly=True, states={'draft': [('readonly', False)]})
    balance_start = fields.Float(
        'Starting Balance', states={'confirm': [('readonly', True)]})
    balance_end = fields.Float(
        'Ending Balance', compute="_end_balance",
        states={'confirm': [('readonly', True)]},
        help="Computed using the cash control lines")
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'cash'))
    line_ids = fields.One2many(
        'cash.line', 'cash_id', string='Transaction en liquide',
        states={'confirm': [('readonly', True)]}, copy=True,
        help='Détails des différentes transactions effectuées')
    state = fields.Selection([
        ('draft', 'New'),
        ('cancel', 'Cancel'),
        ('open', 'Open'),  # used by cash statements
        ('confirm', 'Closed')], default='draft',
        string='Status', required=True, readonly="1", copy=False,
        help=""" When new statement is created the status will be \'Draft\'.\n'
And after getting confirmation from the bank it will be in
\'Confirmed\' status."""),
    currency = fields.Many2one(
        'res.currency', default=lambda self: self._default_currency(),
        string='Currency')

    user_id = fields.Many2one(
        'res.users', required=True, string='Responsable',
        help='Responsable de la caisse')
    opened_date = fields.Date(
        string='Date ouverture', default=fields.Date.context_today,
        help='Date ouverture')
    closing_date = fields.Date(string='Date fermeture')
    state = fields.Selection(
        [('draft', 'Nouveau'), ('open', 'Ouvert'), ('closed', 'Ferme')],
        required=True, readonly="1", copy=False, string='Status')

    @api.multi
    def cash_close(self):
        for cash in self:
            if self.journal_id.type == 'cash':
                cash.write({'state': 'confirm'})
            else:
                raise ValidationError(
                    _("""Can't close a cash register link
to a journal where type is't 'cash'"""))
        return self

    def check_status_condition(self):
        return self.state in ('draft', 'open')

    @api.multi
    def button_cancel(self):
        for cash in self:
            cash.write({'state': 'cancel'})
        return self

    @api.multi
    def button_open(self):
        for cash in self:
            if cash.state != "draft":
                raise UserError(_("You can only open a draft cashbox"))
            cash.write({'state': 'open'})
        return self
