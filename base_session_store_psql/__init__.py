import openerp
def post_load():
    if not openerp.tools.config.get('log_db'):
        raise openerp.exceptions.UserError(
                'You have to define a log_db value in the config to use the'
                'Postgres Session Store.')



    import http
