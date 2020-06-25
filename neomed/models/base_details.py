from odoo import fields, models


class Mothers(models.Model):
    _name = 'neomed.mothers'
    # _inherit = 'mail.thread'
    _description = 'Patients Record'

    histoty_number = fields.Integer(string='Номер истории')
    name = fields.Char(string='ФИО мамы')
    birth_day = fields.Date(string='Дата рождения')
    birth_time = fields.Char(string='Время рождения')
    anamnez = fields.Text(string='Анамнез мамы')
    sex = fields.Selection([
        ('male', 'мужской'),
        ('fermale', 'женский')], string='Пол ребенка')
    birth_namber = fields.Integer('Роды по счету')
    pregnancy_namber = fields.Integer('Беременность по счету')
    severity = fields.Selection([('satisfactory', 'удовлетворительное'), ('moderate_сondition', 'средней тяжести'),
                                 ('severe_condition', 'тяжелое')], string="Состояние при рождении")



    massa_birth = fields.Char(string='Масса при рождении')
    height_birth = fields.Integer(string='Рост')
    OG_birth = fields.Integer(string='Окружность головы')
    OGK_birth = fields.Integer(string='Окружность грудной клетки')
    main = fields.Selection([('main1', 'Новорожденный из группы риска по перинатальной патологии'),
                             ('main2', 'Церебральная ишемия 1 степени, острый период, синдром угнетения ЦНС'),
                             ('main3', 'Респираторный дистресс-синдром новорожденных'),
                             ('main4', 'Недоношенный новорожденный'),
                             ('main5', 'Медикаментозная депрессия дыхательного центра'),
                             ('main6', 'Транзиторное тахипное новорожденного')], string='Диагноз основной')



    main1 = fields.Selection([('main11', 'Дыхательная недостаточность 1 ст'),
                             ('main22', 'Дыхательная недостаточность 2 ст'),
                             ('main33', 'Дыхательная недостаточность 3 ст')], string='Осложение основного')
    main2 = fields.Char(string='Сопутствующий диагноз')


    birth_day_kid = fields.Date(string='Дата рождения')
    severity_kid = fields.Selection([('satisfactory', 'удовлетворительное'), ('moderate_сondition', 'средней тяжести'),
                                 ('severe_condition', 'тяжелое')], string="Состояние при рождении")