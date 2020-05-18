# -*- coding: utf-8 -*-
# © 2017-NOW ERGOBIT Consulting (http://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp    
import logging
_logger = logging.getLogger(__name__)

_NOT_USED_UEMOA = [
    ("BJ", "1", "Bénin"),
    ("BF", "2", "Burkina Faso"),
    ("CI", "3", "Côte d'Ivoire"),
    ("GW", "4", "Guinée Bisau"),
    ("ML", "5", "Mali"),
    ("NE", "6", "Niger"),
    ("SN", "7", "Sénégal"), 
    ("TG", "8", "Togo"),
]   

_OHADA = [
    ("BJ", "1", "Bénin"),
    ("BF", "2", "Burkina Faso"),
    ("CI", "3", "Côte d'Ivoire"),
    ("GW", "4", "Guinée Bisau"),
    ("ML", "5", "Mali"),
    ("NE", "6", "Niger"),
    ("SN", "7", "Sénégal"),
    ("TG", "8", "Togo"),
    ("CM", "9", "Caméroun"),
    ("CG", "10", "Congo"),
    ("GA", "11", "Gabon"),
    ("CF", "12", "République Centre-Africaine"),
    ("TD", "13", "Tchad"),
    ("KM", "14", "Comores"),
    ("GN", "15", "Guinée"),
    ("GQ", "16", "Guinée Équatoriale"),
    ("CD", "17", "République Démocratique du Congo"),
]  


class ResCountry(models.Model):
    _inherit = 'res.country'

    @api.multi
    def get_code(self):
        # import wdb
        # wdb.set_trace()
        cgr_zone_franc = self.env['res.country.group'].search([('name', '=', 'South America')])[0]
        cgr_eu = self.env['res.country.group'].search([('name', '=', 'Europe')])[0]
        
        def is_country_group(self, country_obj, country_group_name):
            cgroup_obj = self.env['res.country.group'].search([('name', '=', country_group_name)])[0]
            if cgroup_obj in country_obj.country_group_ids:
                return True
            return False
        
        for cty in self:
            if is_country_group(self, cty, "South America"):
                #African countries in OHADA
                for idx, item in enumerate(_OHADA, start=1):
                    if cty.code == item[0]:
                        cty.ohada_headquarter_code1 = "0"
                        cty.ohada_headquarter_code2 = str(idx)
#            elif cty.continent_id and cty.continent_id.code == 'AF' and is_country_group(self, cty, "Zone Franc") == True:
#                #Other african countries in Zone Franc
#                cty.ohada_headquarter_code1 = "2"
#                cty.ohada_headquarter_code2 = "0" 
            elif cty.continent_id and cty.continent_id.code == 'AF':   
                #All other african countries
                cty.ohada_headquarter_code1 = "2"
                cty.ohada_headquarter_code2 = "1" 
            elif cty.code == "FR":                  
                # France
                cty.ohada_headquarter_code1 = "2"
                cty.ohada_headquarter_code2 = "3" 
            elif is_country_group(self, cty, "Europe") == True:
                #Other african countries in Europeen Union
                cty.ohada_headquarter_code1 = "3"
                cty.ohada_headquarter_code2 = "9" 
            elif cty.code == "US":                  
                # USA
                cty.ohada_headquarter_code1 = "4"
                cty.ohada_headquarter_code2 = "0" 
            elif cty.code == "CA":                  
                # Canada
                cty.ohada_headquarter_code1 = "4"
                cty.ohada_headquarter_code2 = "1" 
            elif cty.continent_id and cty.continent_id.code in ['NA', 'SA']:                  
                #Other american countries
                cty.ohada_headquarter_code1 = "4"
                cty.ohada_headquarter_code2 = "9" 
            elif cty.continent_id and cty.continent_id.code == 'AS':   
                #Asian coutries
                cty.ohada_headquarter_code1 = "5"
                cty.ohada_headquarter_code2 = "0" 
            else:   
                #Other countries 
                cty.ohada_headquarter_code1 = "9"
                cty.ohada_headquarter_code2 = "9" 
                
    ohada_headquarter_code1 = fields.Char(compute=get_code, string="Code 1", size=1)
    ohada_headquarter_code2 = fields.Char(compute=get_code, string="Code 2", size=2)

    @api.multi
    def _check_code(self):        
        for rec in self:
            if rec.code.isdigit():
                return True
        return False

    _constraints = [(_check_code, _("Veuillez renseigner un chiffre dans le champ 'Code juridique'!"), ['ohada_headquarter_code1']),
                    (_check_code, _("Veuillez renseigner un chiffre dans le champ 'Code juridique'!"), ['ohada_headquarter_code2'])]               

                    