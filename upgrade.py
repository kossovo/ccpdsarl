# -*- python -*-
"""This is a template upgrade script.

The purpose is both to cover the most common use-case (updating all modules)
and to provide an example of how this works.
"""


def run(session, logger):
    """Update all modules."""
    db_version = session.db_version

    if session.is_initialization:
        logger.warn("Usage of upgrade script for initialization detected. "
                    "You should consider customizing the present upgrade "
                    "script to add modules install commands. The present "
                    "script is at : %s (byte-compiled form)",
                    __file__)
        return

    if db_version and db_version.vstring == '3.0':
        fix_default_property_account(session, logger)
        # FIXME - Corriger l'erreur qui survient a l'appel de cette fonction
        # delete_anytracker_invoicing_old_view(session, logger)


def delete_anytracker_invoicing_old_view(session, logger):
    """
    Supprime les vues obsolètes du module "anytracker" liée à la facturation
    """
    xml_ids = [
        "invoicing_ticket_view_form",
        "invoicing_bouquet_form",
        "invoicing_ticket_view_search",
        "priority_form_with_invoicing",
        "priority_tree_with_invoicing"
    ]

    invoicing_model_data = session.env['ir.model.data'].search([
        ('model', '=', 'ir.ui.view'),
        ('module', '=', 'anytracker'),
        ('name', 'in', xml_ids),
    ])

    for imd in invoicing_model_data:
        view = session.env['ir.ui.view'].browse(imd.res_id)
        view.unlink()

        logger.info('Deleting %s' % imd.name)


def fix_default_property_account(session, logger):
    """
    Après la migration, les comptes clients par defauts de plusieurs clients
    et fournisseurs ne sont plus affectés.
    Ce script permet donc de les réaffecter
    """
    customer_to_fix = session.env['res.partner'].search([
        ('customer', '=', True),
        ('property_account_receivable_id', '=', False),
        ('property_account_payable_id', '=', False)
    ])

    default_account_receivable = session.env['account.account'].search([
        ('code', '=', '411700')], limit=1)

    default_account_payable = session.env['account.account'].search([
        ('code', '=', '401700')], limit=1)

    for customer in customer_to_fix:
        if not customer.property_account_receivable_id:
            customer.write({
                'property_account_receivable_id': default_account_receivable})
        if not customer.property_account_payable_id:
            customer.write({
                'property_account_payable_id': default_account_payable})
        logger.info('Fix default account property for customer %s' % customer.name)

    # logger.info("Default upgrade procedure : updating all modules.")
    # session.update_modules(['all'])
