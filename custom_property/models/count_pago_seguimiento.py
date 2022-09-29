
#-*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api,_
from odoo.exceptions import UserError

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
class Rent_type_get(models.Model):

	_inherit="rent.type"

	renttype = fields.Selection(selection_add=[('Day', 'Dia')])

	@api.constrains('sequence_in_view')
	def _check_value(self):
		pass


class Landlord_partner_hp(models.Model):

	_inherit='tenancy.rent.schedule'

	hecho_pago = fields.Char(string='H/P')


	def create_invoice(self):
		res=super(Landlord_partner_hp,self).create_invoice()
		self.env['account.move'].search([('id','=',self.invc_id.id)]).update({
			'numero_pagos':self.hecho_pago,
			})
		return res

class Account_move_hp(models.Model):

	_inherit='account.move'

	numero_pagos=fields.Char(string='Numero de pago')

class Account_asset_asset_customs(models.Model):

	_inherit='account.asset.asset'

	chech_in = fields.Datetime(string='Chech in')

	chech_out = fields.Datetime(string='Chech out')

	entrega_acceso_id = fields.Many2one('res.partner',string='Entrega de accesos')


class Account_analytic_account_bh(models.Model):

	_inherit='account.analytic.account'

	chech_in = fields.Datetime(string='Check in')

	chech_out = fields.Datetime(string='Check out')

	entrega_acceso_id = fields.Many2one('res.partner',string='Entrega de accesos')

	telefono = fields.Char(string='telefono')

	email = fields.Char(string='Correo')


	@api.onchange('entrega_acceso_id')
	def _onchange_entrega_acceso_id(self):
		self.email=self.entrega_acceso_id.email
		self.telefono=self.entrega_acceso_id.phone

	def create_rent_schedule(self):
		res=super(Account_analytic_account_bh,self).create_rent_schedule()
		self.set_number_pay()
		#raise UserError(len()
		return res

	def set_number_pay(self):
		pago=1
		total_hecho=len(self.rent_schedule_ids)
		for rec in self.rent_schedule_ids:
			rec.hecho_pago=str(pago)+"/"+str(total_hecho)
			pago+=1
    		
	def action_invoice_payment(self):
		inv_obj = self.env['account.move']
		for payment in self.rent_schedule_ids:
			if not payment.invc_id:
				inv_line_values = payment.get_invloice_lines()
				inv_values = {
					'partner_id': payment.tenancy_id.tenant_id.parent_id.id or False,
					'type': 'out_invoice',
					'property_id': payment.tenancy_id.property_id.id or False,
					'invoice_date': datetime.now().strftime(
						DEFAULT_SERVER_DATE_FORMAT) or False,
					'invoice_line_ids': inv_line_values,
					'new_tenancy_id': payment.tenancy_id.id,
					'numero_pagos':payment.hecho_pago,
				}
				invoice_id = inv_obj.create(inv_values)
				payment.write({'invc_id': invoice_id.id, 'inv': True})
		#publicar las facturas	
		for payment in self.rent_schedule_ids:
			inv_obj = self.env['account.move'].search([('id','=',payment.invc_id.id)])
			if inv_obj.state!='posted':
				inv_obj.action_post()
				payment.move_check=True

	def action_quotation_send(self):
		if not self.property_id:
			raise UserError("No cuenta con el remitente ")
		if not self.tenant_id:
			raise UserError("Inquilino esta vacio")
		if not self.entrega_acceso_id:
			raise UserError("Entrega de accesos vacio")

		template_id=self.env.ref('custom_property.email_template_contrato').id
		self.env['mail.template'].browse(template_id).send_mail(self.id,force_send=True)
		
	

