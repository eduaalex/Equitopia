
#-*- coding: utf-8 -*-
from datetime import date, datetime
from re import S

from odoo import models, fields, api,_
from odoo.exceptions import UserError

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
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

	hora_entrada = fields.Float(string='Hora de entrada')

	hora_salida = fields.Float(string='Hora de salida')

	entrega_acceso_id = fields.Many2one('res.partner',string='Entrega de accesos')

	count_reg=fields.Integer(compute="_calculo_registro")

	def _calculo_registro(self):
		"""
		suma la cantidad de eventos de calendario
		"""
		for rec in self:
			rec.count_reg=self.env['calendar.event'].search_count([('property_calendary','=',rec.id)])



class Account_analytic_account_bh(models.Model):

	_inherit='account.analytic.account'

	chech_in = fields.Datetime(string='Check in')

	chech_out = fields.Datetime(string='Check out')

	hora_entrada = fields.Float(string='Hora de entrada')

	hora_salida = fields.Float(string='Hora de salida')

	entrega_acceso_id = fields.Many2one('res.partner',string='Entrega de accesos')

	telefono = fields.Char(string='telefono')

	email = fields.Char(string='Correo')

	chech_in_realizado = fields.Datetime(string='Realizado')

	bandera_in_realizado = fields.Boolean(string='Realizado')

	@api.onchange('bandera_in_realizado')
	def _onchange_bandera_in_realizado(self):
		if self.bandera_in_realizado:
			self.chech_in_realizado=datetime.now()
		else:
			self.chech_in_realizado=False

	chech_out_realizado = fields.Datetime(string='Realizado')

	bandera_out_realizado = fields.Boolean(string='Realizado')

	@api.onchange('bandera_out_realizado')
	def _onchange_bandera_out_realizado(self):
		if self.bandera_out_realizado:
			self.chech_out_realizado=datetime.now()
		else:
			self.chech_out_realizado=False


	@api.onchange('property_id')
	def _onchange_property_id(self):
		self.entrega_acceso_id=self.property_id.entrega_acceso_id.id
		self.email=self.entrega_acceso_id.email
		self.telefono=self.entrega_acceso_id.phone
		self.hora_entrada=self.property_id.hora_entrada
		self.hora_salida=self.property_id.hora_salida


	def set_number_pay(self):
		"""
		crear listado de nombre para la facturacion
		"""
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
					'invoice_date_due':payment.start_date,
				}
				invoice_id = inv_obj.create(inv_values)
				payment.write({'invc_id': invoice_id.id, 'inv': True})
		#publicar las facturas	
		for payment in self.rent_schedule_ids:
			inv_obj = self.env['account.move'].search([('id','=',payment.invc_id.id)])
			if inv_obj.state!='posted':
				inv_obj.action_post()
				payment.move_check=True
	
	def action_invoice_tenancy(self):
		for invoice_teancy in self.rent_schedule_ids:
			if invoice_teancy.tenancy_id.is_landlord_rent:
				account_jrnl_obj = self.env['account.journal'].search(
					[('type', '=', 'purchase')], limit=1)
				inv_lines_values = {
                # 'origin': 'tenancy.rent.schedule',
                'name': 'Rent Cost for' + invoice_teancy.tenancy_id.name,
                'quantity': 1,
                'price_unit': invoice_teancy.amount or 0.00,
                'account_id':
                    invoice_teancy.tenancy_id.property_id.expense_account_id.id or False,
                'analytic_account_id': invoice_teancy.tenancy_id.id or False,
           		}
				owner_rec = invoice_teancy.tenancy_id.property_owner_id
				invo_values = {
                'partner_id': invoice_teancy.tenancy_id.property_owner_id.id or False,
                'type': 'in_invoice',
                'invoice_line_ids': [(0, 0, inv_lines_values)],
                'property_id': invoice_teancy.tenancy_id.property_id.id or False,
                'invoice_date': invoice_teancy.start_date or False,
                # 'schedule_id': self.id,
                'new_tenancy_id': invoice_teancy.tenancy_id.id,
                'journal_id': account_jrnl_obj.id or False
				 }
				acc_id = self.env['account.move'].create(invo_values)
				invoice_teancy.write({'invc_id': acc_id.id, 'inv': True})
		#publicar las facturas	
		for payment in self.rent_schedule_ids:
			inv_obj = self.env['account.move'].search([('id','=',payment.invc_id.id)])
			if inv_obj.state!='posted':
				inv_obj.action_post()
				payment.move_check=True
	
	def button_cancel_tenancy(self):
		res=super(Account_analytic_account_bh,self).button_cancel_tenancy()
		self.env['alert.clock'].search([('contratos_id','=',self.id)]).unlink()
		self.env['calendar.event'].search([('property_tanency','=',self.id)]).unlink()
		return res

	def button_start(self):
		res=super(Account_analytic_account_bh,self).button_start()
		if not self.property_owner_id:
			raise UserError("El campo de dueño esta vacio")
		data={
            'actividad':'new_tenancy',
            'propiedad_id':self.property_id.id,
            'contratos_id':self._origin.id,
            'duenos_id':self.property_owner_id.id
        }
		self.env['alert.clock'].create(data)
		partner_ids=self.env.user.partner_id.ids
		if self.manager_id:
			partner_ids.append(self.manager_id.partner_id.id)
		if self.property_owner_id:
			partner_ids.append(self.property_owner_id.parent_id.id)
		
		data_calendary={
        'name':self.property_id.name+":"+self.code+"/"+self.tenant_id.name,
        'partner_ids':partner_ids,
		  'start_date':self.date_start,
        'stop_date':self.date, 
        'start':self.date_start,
        'stop':self.date,
        'allday':True,
        'property_calendary':self.property_id.id,  
        'property_tanency':self.id,
        }
		self.env['calendar.event'].create(data_calendary)
		return res
				

	def action_quotation_send(self):
		"""
		envia correo electronico de los contratos de inquilino
		valida sus respetivos remitentes y destinatarios
		"""
		if not self.manager_id:
			raise UserError("No cuenta con el remitente ")
		if not self.tenant_id:
			raise UserError("Inquilino esta vacio")
		if not self.entrega_acceso_id:
			raise UserError("Entrega de accesos vacio")

		template_id=self.env.ref('custom_property.email_template_contrato').id
		self.env['mail.template'].browse(template_id).send_mail(self.id,force_send=True)

	def action_tenancy_send(self):
		"""
		Envia correo electronico de los contratos de propietario
		valida sus respetivos remitentes y destinatarios
		"""
		if not self.property_owner_id:
			raise UserError("No cuenta con el remitente ")
		if not self.contact_id:
			raise UserError("Contacto esta vacio")
		if not self.manager_id:
			raise UserError("Gerente de cuentas o remitente vacio")

		template_id=self.env.ref('custom_property.email_template_contrato_tenancy').id
		self.env['mail.template'].browse(template_id).send_mail(self.id,force_send=True)


	def create_rent_schedule(self):
		"""
        This button method is used to create rent schedule Lines.
        @param self: The object pointer
        """
		rent_obj = self.env['tenancy.rent.schedule']
		for tenancy_rec in self:
			if tenancy_rec.rent_type_id.renttype == 'Weekly':
				d1 = tenancy_rec.date_start
				d2 = tenancy_rec.date
				interval = int(tenancy_rec.rent_type_id.name)
				if d2 < d1:
					raise Warning(
                        _('End date must be greater than start date.'))
				wek_diff = (d2 - d1)
				wek_tot1 = (wek_diff.days) / (interval * 7)
				wek_tot = (wek_diff.days) % (interval * 7)
				if wek_diff.days == 0:
					wek_tot = 1
				if wek_tot1 > 0:
					for wek_rec in range(int(wek_tot1)):
						rent_obj.create(
                            {'start_date': d1,
                             'amount': tenancy_rec.rent * interval or 0.0,
                             'property_id': tenancy_rec.property_id
                                and tenancy_rec.property_id.id or False,
                             'tenancy_id': tenancy_rec.id,
                             'currency_id': tenancy_rec.currency_id.id
                                or False,
                             'rel_tenant_id': tenancy_rec.tenant_id.id
                             })
						d1 = d1 + relativedelta(days=(7 * interval))
				if wek_tot > 0:
					one_day_rent = 0.0
					if tenancy_rec.rent:
						one_day_rent = (tenancy_rec.rent) / (7 * interval)
					rent_obj.create(
                        {'start_date': d1.strftime(
                            DEFAULT_SERVER_DATE_FORMAT),
                         'amount': (one_day_rent * (wek_tot)) or 0.0,
                         'property_id': tenancy_rec.property_id
                            and tenancy_rec.property_id.id or False,
                         'tenancy_id': tenancy_rec.id,
                         'currency_id': tenancy_rec.currency_id.id or False,
                         'rel_tenant_id': tenancy_rec.tenant_id.id
                         })
			elif tenancy_rec.rent_type_id.renttype != 'Weekly' and tenancy_rec.rent_type_id.renttype != 'Day':
				if tenancy_rec.rent_type_id.renttype == 'Monthly':
					interval = int(tenancy_rec.rent_type_id.name)
				if tenancy_rec.rent_type_id.renttype == 'Yearly':
					interval = int(tenancy_rec.rent_type_id.name) * 12
				d1 = tenancy_rec.date_start
				d2 = tenancy_rec.date
				diff = abs((d1.year - d2.year) * 12 + (d1.month - d2.month))
				tot_rec = diff / interval
				tot_rec2 = diff % interval
				if abs(d1.month - d2.month) >= 0 and d1.day < d2.day:
					tot_rec2 += 1
				if diff == 0:
					tot_rec2 = 1
				if tot_rec > 0:
					for rec in range(int(tot_rec)):
						rent_obj.create(
                            {'start_date': d1,
                             'amount': tenancy_rec.rent * interval or 0.0,
                             'property_id': tenancy_rec.property_id
                                and tenancy_rec.property_id.id or False,
                             'tenancy_id': tenancy_rec.id,
                             'currency_id': tenancy_rec.currency_id.id
                                or False,
                             'rel_tenant_id': tenancy_rec.tenant_id.id
                             })
						d1 = d1 + relativedelta(months=interval)
				if tot_rec2 > 0:
					rent_obj.create({
                        'start_date': d1,
                        'amount': tenancy_rec.rent * tot_rec2 or 0.0,
                        'property_id': tenancy_rec.property_id
                        and tenancy_rec.property_id.id or False,
                        'tenancy_id': tenancy_rec.id,
                        'currency_id': tenancy_rec.currency_id.id or False,
                        'rel_tenant_id': tenancy_rec.tenant_id.id
                    })
			if tenancy_rec.rent_type_id.renttype == 'Day':
				d1 = tenancy_rec.date_start
				d2 = tenancy_rec.date
				wek_diff = (d2 - d1)
				dia_recod=0	
				while dia_recod<wek_diff.days:
					rent_obj.create({
                        'start_date': d1,
                        'amount': tenancy_rec.rent or 0.0,
                        'property_id': tenancy_rec.property_id
                        and tenancy_rec.property_id.id or False,
                        'tenancy_id': tenancy_rec.id,
                        'currency_id': tenancy_rec.currency_id.id or False,
                        'rel_tenant_id': tenancy_rec.tenant_id.id
                    })		
					interval=int(self.rent_type_id.name)			
					d1=d1+relativedelta(days=interval)
					dia_recod+=interval			

			self.set_number_pay()		
			return tenancy_rec.write({'rent_entry_chck': True})	

