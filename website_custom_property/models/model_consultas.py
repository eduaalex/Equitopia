#-*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError
class Website_consult(models.Model):

    _name='alert.clock'

    _rec_name="duenos_id"

    actividad=fields.Selection(
        string='Actividad',
        selection=[
                 ('new_payment', 'Nuevo pago'),
                 ('new_tenancy', 'Nuevo contrato'),
                 ('delivery', 'Entrega'),
             
        ],
        )
    
    propiedad_id = fields.Many2one('account.asset.asset',string='Propiedad')

    contratos_id = fields.Many2one('account.analytic.account',string='Contratos')

    duenos_id = fields.Many2one('landlord.partner',string='Dueños')

    
class Website_payment_tenancy(models.Model):

    _inherit='account.payment'

    def post(self):
        res=super(Website_payment_tenancy,self).post()
        self.env['alert.clock'].create({
            'actividad':'new_payment',
            'propiedad_id':self.property_id.id,
            'contratos_id':self.tenancy_id.id,
            'duenos_id':self.property_id.property_owner.id,
        })
        return res






    

