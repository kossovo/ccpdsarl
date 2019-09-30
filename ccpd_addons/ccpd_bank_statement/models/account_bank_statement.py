#!/usr/bin/env python
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountBankStatement(models.Model):
    """
    Surcharge de la gestion des relevés bancaires pour qu'elles fonctionnent
    comme la caisse dans la version 8.0
    """
    _inherit = 'account.bank.statement'
