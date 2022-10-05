
#-*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class Tenant_partner_user(models.Model):

    _inherit="tenant.partner"

    portal_activo=fields.Boolean(string='Portal')

    bandera_portal=fields.Boolean(string='Portal',compute="_no_interno")
    def _no_interno(self):
        group_internal=self.env.ref('base.group_user')
        res_tenant=self.env['res.users'].search([('tenant_id','=',self.id)])
        res_tenant.write({'groups_id': [(3, group_internal.id)]})
        self.bandera_portal=False

    def active_portal(self):    
        group_portal=self.env.ref('base.group_portal')
        res_tenant=self.env['res.users'].search([('tenant_id','=',self.id)])
        res_tenant.write({'groups_id': [(4, group_portal.id)]})
        self.portal_activo=True
        
class Landlord_partner_list(models.Model):

    _inherit="landlord.partner"
        
    partner_property_ids = fields.One2many(
        'property.usuers',
        'line_property_id',
        string='Propiedades de Usuario',
    )

    def ver_propiedades(self):        
        propiedades=self.env['account.asset.asset'].search([('property_owner','=',self.id)])
        for item in propiedades:
            bandera_busqueda=False            
            for list_all in self.partner_property_ids:
                if list_all.nombre.id==item.id:
                    lista_data={
                    'partner_property_ids':[(1,list_all.id,{
                        'nombre':item.id,
                        'tipo_alquile_id':item.rent_type_id.id,
                        'img_propiedad':item.image,
                        'alquiler':item.ground_rent,
                        'state':item.state
                        })]
                    }
                    self.write(lista_data)                    
                    bandera_busqueda=True

            if not bandera_busqueda:
                lista_data={
                'partner_property_ids':[(0,0,{
                    'nombre':item.id,
                    'tipo_alquile_id':item.rent_type_id.id,
                    'img_propiedad':item.image,
                    'alquiler':item.ground_rent,
                    'state':item.state
                    })]
                }
                self.write(lista_data)


class Landlord_partner_property_lines(models.Model):

    _name = 'property.usuers'

    nombre = fields.Many2one('account.asset.asset',string='Propiedad')

    img_propiedad = fields.Binary(string='Imagen de propiedad',attachment=True)

    tipo_alquile_id = fields.Many2one('rent.type',string='Tipo de Alquiler')

    alquiler = fields.Integer(string='Alquiler')

    state=fields.Selection(
        string='Estado',
        selection=[
                 ('new_draft', 'Reserva abierta'),
                 ('draft', 'Disponible'),
                 ('book', 'Reservada'),
                 ('normal', 'En Arrendamiento'),
                 ('close', 'Rebaja'),
                 ('sold', 'Vendida'),
                 ('open', 'Correr'),
                 ('cancel', 'Cancelar')
        ],
        )


    line_property_id = fields.Many2one('landlord.partner',string='Propiedades')









