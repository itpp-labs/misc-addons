# -*- coding: utf-8 -*-
# © 2017-NOW ERGOBIT Consulting (http://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp    
import logging
_logger = logging.getLogger(__name__)
   

class CompanyLegalForm(models.Model):
    _name = 'company.legal.form'
    _description = u"Forme Juridique"
    _order = "code"

    name = fields.Char(string='Désignation', required=True)
    shortcut = fields.Char(string='Abbréviation')
    code = fields.Char(string="Code juridique", size=1, required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', "Cette forme juridique existe déjà!"),
            ('code_uniq', 'unique (code)', "Ce code existe déjà!"),
            ('shortcut_uniq', 'unique (shortcut)', "Cette abréviation existe déjà!")]

    @api.multi
    def _check_code(self):        
        for rec in self:
            if rec.code.isdigit():
                return True
        return False

    _constraints = [(_check_code, _("Veuillez renseigner un chiffre dans le champ 'Code juridique'!"), ['code'])]               

    @api.multi
    def name_get(self):
        res = []
        for clf in self:
            name = clf.name
            if clf.shortcut:
                name = u'%s (%s)' % (clf.name, clf.shortcut)
            res.append((clf.id, name))
        return res
    

class CompanySector(models.Model):
    _name = 'company.sector'
    _description = u'Secteur économique'
    _order = "code asc"

    code = fields.Char(string='Code du secteur', size=3, required=True)
    name = fields.Char(string='Désignation du secteur', required=True)
    activity_ids = fields.One2many(
        'company.activity', 'sector_id', string="Activité économique")        
    
    @api.multi
    def name_get(self):
        res = []
        for sec in self:
            name = sec.name
            if sec.code:
                name = u'%s %s' % (sec.code, sec.name)
            res.append((sec.id, name))
        return res

        
class CompanyActivity(models.Model):
    _name = 'company.activity'
    _description = u"Activité économique"
    _order = "full_code asc"

    @api.multi
    @api.depends('code', 'sector_id', 'sector_id.code')
    def get_full_code(self):
        for act in self:
            if act.sector_id.code and act.code:
                act.full_code = str(act.sector_id.code) + " " + str(act.code)

    code = fields.Char(string="Code de l'activité", size=3, required=True)
    full_code = fields.Char(compute=get_full_code, 
        string="Code complet de l'activité", size=7, read_only=True, store=True)
    name = fields.Char(string="Désignation de l'activité", required=True)
    sector_id = fields.Many2one('company.sector', 
        string="Secteur économique", ondelete='restrict', required=True)

    @api.multi
    def name_get(self):
        res = []
        for act in self:
            name = act.name
            if act.full_code:
                name = u'%s %s' % (act.full_code, act.name)
            res.append((act.id, name))
        return res
                                              
                                              
class ResCompanyActivity(models.Model):
    _name = "res.company.activity"
    _description = u"Activité économique"
    
    @api.model
    def get_company(self):
        company_id = self.env['res.users'].browse(self._context['uid']).company_id.id
        return company_id
    
    company_id = fields.Many2one('res.company', 'Société', default=get_company)
    activity_id = fields.Many2one('company.activity', 'Activité économique')
    main_activity = fields.Boolean("Activité principale")
    turnover_amount  = fields.Float("Chiffre d'affaire HT", digits=dp.get_precision('Ergobit'))
    turnover_percentage = fields.Float("% de l'activité dans le CA", digits=dp.get_precision('Ergobit Rate'))
    surplus_amount = fields.Float("Valeur ajoutée", digits=dp.get_precision('Ergobit'))
    surplus_percentage = fields.Float("% de l'activité dans la VA", digits=dp.get_precision('Ergobit Rate'))
    amount_reported = fields.Selection(selection=[('turnover_amount',"Chiffre d'affaire"), 
                                                  ('surplus_amount',"Valeur ajoutée")], string='Montant reporté')
                                       
                                       
class ResCompanyEquity(models.Model):
    _name="res.company.equity"
    _description = u"Actionariat/Participation"
    _order = "capital_percentage desc"
    
    @api.model
    def get_company(self):
        company_id = self.env['res.users'].browse(self._context['uid']).company_id.id
        return company_id

    @api.model
    def get_company_currency(self):
        currency_id = self.env['res.users'].browse(self._context['uid']).company_id.currency_id.id
        return currency_id

    company_id = fields.Many2one('res.company','Company', default=get_company)
    partner_id = fields.Many2one('res.partner', required=True, string='Partenaire', domain=[('company_type', '=', 'company')])
    type = fields.Selection(selection=[('shareholder','Actionnaire/Associé'), ('affiliate',"Filiale/Participation")], string='Type', required=True)
    capital_amount = fields.Float('Capital', required=True, digits=dp.get_precision('Ergobit'))    
    capital_percentage = fields.Float("Pourcentage du capital total", required=True, digits=dp.get_precision('Ergobit'))
    currency_id = fields.Many2one("res.currency", string="Devise", default=get_company_currency, required=True)


class ResCompanyManager(models.Model):
<<<<<<< HEAD
    _name="res.company.manager"
=======
    _name = "res.company.manager"
>>>>>>> Artem/12.0-ohada-modules
    _description = u"Executive/Adminstrative"
    
    @api.model
    def get_company(self):
        company_id = self.env['res.users'].browse(self._context['uid']).company_id.id
        return company_id

    company_id = fields.Many2one('res.company','Company', default=get_company)
    manager_id = fields.Many2one('res.partner', required=True, string='Manager', domain=[('company_type', '=', 'person')], ondelete='restrict')
    type = fields.Selection(selection=[('executive',"Dirigeant de l'entreprise"), ('administrative',"Membre du CA")], string='Type', required=True)
    function = fields.Char('Qualité', related='manager_id.function')
    vat = fields.Char('Id. fiscale (NINEA)', related='manager_id.vat')
    contact_address = fields.Char('Adresse', related='manager_id.contact_address')
    
    
class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.multi
    @api.depends('legal_form_id', 'legal_form_id.code')
    def get_code(self):
        for cpy in self:
            if cpy.legal_form_id:
                cpy.legal_form_code = str('1' if cpy.priority_agreement else '0') + " " + str(cpy.legal_form_id.code)   
    
    @api.multi
    @api.depends('country_id', 'affiliate_ids', 'affiliate_ids.partner_id', 'affiliate_ids.partner_id.country_id')
    def get_affiliate_count(self):
        in_count = out_count = 0
        for cpy in self:
            for aff in cpy.affiliate_ids:
                if aff.partner_id and aff.partner_id.country_id and cpy.country_id:
                    if aff.partner_id.country_id == cpy.country_id:
                        in_count += 1
                    else:
                        if aff.partner_id.has_own_accounting:
                            out_count += 1
            cpy.num_affiliates_in_country = in_count        
            cpy.num_affiliates_out_country = out_count        

    @api.model
    def get_country_sn(self):
        return self.env['res.country'].search([('code', '=', 'SN')])[0]
                       
    legal_name = fields.Char("Dénomination sociale", default=lambda self: self.env['res.users']._get_company().name)
    ninea = fields.Char("Id. fiscale (NINEA)")
    rccm = fields.Char("Régistre du commerce")
    social_registry_id = fields.Char('N° de caisse social')
    acronym = fields.Char('Sigle usuel')
    code_importer = fields.Char('Code Importateur')
    office = fields.Char('Greffe', size=5, default='0')
    first_fiscalyear_in_country = fields.Char("Première année d'exercice dans le pays", size=4)
    controlled_by = fields.Selection(selection=[('A','public'), ('B',"privé national"), 
        ('C',"privé étranger")], string='Entreprise sous contrôle')
    activity_ids = fields.One2many('res.company.activity',   
        'company_id', string="Activités de l'entreprise")        
    shareholder_ids = fields.One2many('res.company.equity', 'company_id',
        string="Actionnaires/Associés", domain=[('type', '=', 'shareholder')])
    affiliate_ids = fields.One2many('res.company.equity', 'company_id', 
        string="Filiales/Participations", domain=[('type', '=', 'affiliate')])        
    priority_agreement = fields.Boolean(string="Agrément prioritaire", 
        help="Cocher, si l'entreprise bénéficie d'un aggrément prioritaire")
    legal_form_id = fields.Many2one('company.legal.form', 'Forme juridique')
    legal_form_code = fields.Char(string="Code forme juridique", size=3, compute=get_code)
    fiscal_regime = fields.Selection(selection=[('1','Réel normal'), ('2',"Réel simplifé"), 
        ('3',"Synthétique"), ('3',"Forfait")], string='Régime fiscal')
    executive_ids = fields.One2many('res.company.manager', 'company_id', 
                string="Dirigeants de l'entreprise", domain=[('type', '=', 'executive')])        
    administrative_ids = fields.One2many('res.company.manager', 'company_id', 
                string="Membres du CA", domain=[('type', '=', 'administrative')])        
    num_affiliates_in_country = fields.Integer("Nombre de filiales dans le pays", compute=get_affiliate_count)
    num_affiliates_out_country = fields.Integer("Nombre de filiales hors du pays", compute=get_affiliate_count)
    headquarters_country_id = fields.Many2one("res.country", "Pays du siège social", default=get_country_sn)
    headquarters_country_code1 = fields.Char(
        related='headquarters_country_id.ohada_headquarter_code1', string='HQ Code 1', readonly=True)
    headquarters_country_code2 = fields.Char(
        related='headquarters_country_id.ohada_headquarter_code2', string='HQ Code 2', readonly=True)



''' Brauche ich den Rest ab hier???  -> Prüfen

class frontpage(models.Model):
    _name = "frontpage"
    
    @api.model
    def get_company(self):
        company_id = self.env['res.users'].browse(self._context['uid']).company_id.id
        return company_id
    
    @api.model
    def get_fiscalyear(self):
        fiscalyear_id = self.env['account.fiscalyear'].find()
        return fiscalyear_id
    
    @api.multi
    def _check_company_fiscalyear(self):
        search_id = [rec.id for rec in self.search([])]
        search_id.remove(self.ids[0])
        for rec in self.browse(self.ids):
            for line in self.browse(search_id):
                if rec.company_id.id == line.company_id.id and rec.fiscalyear.id == line.fiscalyear.id:
                    return False
        return True
    
    company_id = fields.Many2one('res.company','Company', default=get_company)
    fiscalyear = fields.Many2one('account.fiscalyear','Fiscalyear' , default=get_fiscalyear)
    actual_closing_date = fields.Date('Actual Closing Date')
    perc_production_capa_used = fields.Float('Perc Production Capa Used')
    contact_person = fields.Many2one('hr.employee','Contact Person')
    professional_person = fields.Many2one('hr.employee','Professional Person')
    public_accountant_1 = fields.Many2one('res.partner','Public Accountant 1')
    public_accountant_2 = fields.Many2one('res.partner', 'Public Accountant 2')
    certified = fields.Selection([('A','NOn assujetti'),('B','Non (refus)'),('C','Oui avecreserv'),('D', 'Ouisans reserves')],'Certified')
    approved = fields.Selection([('A','Non assujetti'), ('B','Non'), ('C','Oui')],'Approved')
    signee = fields.Many2one('hr.employee','Signee')
    signing_date = fields.Date('Signing Date')
    
    _constraints = [(_check_company_fiscalyear,_('Vous avez pour ce tableau un autre rapport en cours dans cet exercice fisal. Veuillez continuer avec celui ci.'),['company_id'])] 
    
  
class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    firstname = fields.Char('Name')
    lastname = fields.Char('Lastname')
    
    @api.model
    def create(self, values):
        # Create same Employee automatically when create new user.
        if values.get('firstname') and values.get('lastname'):
            name = values.get('firstname') + ' ' + values.get('lastname')
            values.update({'name' : name})
            return super(hr_employee, self).create(values)
    
    _sql_constraints = [("company_must_unique","unique(company_id)","Company Must be Unique")]
  
    
class res_user_name(models.Model):
    _inherit = 'res.users'
    
    name = fields.Char('Name', required=True, select=True, default=" ")
    firstname = fields.Char('Firstname')
    lastname = fields.Char('Lastname')
    
    @api.multi
    def user_full_name(self, firstname, lastname):
        res = {}
        if firstname or lastname:
            full_name = str(firstname) + " " + str(lastname)
            res.update({'name':full_name})
        else:
            res.update({'name':" "})
        return {'value':res}
    
    @api.model
    def create(self, values):
        # Create same Employee automatically when create new user.
        if values.get('firstname') and values.get('lastname'):
            name = values.get('firstname') + ' ' + values.get('lastname')
            values.update({'name' : name})
            print "sbssackcawsc",values
            self.env['hr.employee'].create(values)
            return super(res_user_name, self).create(values)
                                               
'''        