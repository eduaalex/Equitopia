
#-*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError

#cuando son pago o salida de dinera hay quecambiar el tipo de fectura
#que en ves de que creen unfactura de cliente denbe crearuna factruade proveeodor

class Balance_economico_lines(models.Model):

	_name="balance.economyc.report"

	_rec_name="property_mov_id"

	balance_economico_ids = fields.One2many(
	    'balance.economyc.report.lines',
	    'balance_economyc_lines_id',
	    string='Balance Economico',
	)

	property_mov_id = fields.Many2one(
	    'account.asset.asset',
	    string='Propiedad',
	)

	company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.user.company_id)

	currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        string='Currency',
        required=True)

	def actualizar_balecon(self):
		propiedades=self.env['account.asset.asset'].search([])
		for pd in propiedades:
			data=self.env['account.payment'].search([('property_id','=',pd.id),
			('calc_balance','=',False),('state','<>','draft')],order='payment_date asc')
			raise UserError(str(data))
			data_balance=[]	

			array_data=[]
			acum_mov=0.0
			for item in data: #recorre toda la informacion de pagos de la propiedad
				cantidad=0.0
				if item.payment_type=='outbound':
					cantidad=item.amount*-1
					array_data.append(cantidad)
					acum_mov=acum_mov-item.amount
				else:
					cantidad=item.amount
					array_data.append(cantidad)
					acum_mov=acum_mov+item.amount

				text_descrip=''
				for inv_fac in item.invoice_ids:
					for line in inv_fac.invoice_line_ids:
						text_descrip=line.name+'\n'
				data_balance.append((0,0,
					{
						 'property_mov_id':item.property_id.id,
						 'date_mov':item.payment_date,
						 'type_mov':item.payment_type,
						 'type_payment':item.tipo_de_pago,
						 'cant_mov':cantidad,
						 'acum_mov':acum_mov,
						 'decription_mov':item.communication,
						 'payment_mov_id':item.id,
						 'currency_id':item.currency_id.id or False,
						 'line_invoice':text_descrip,
					}
					))
				item.calc_balance=True

			#crear nuevo balanc
			
			self.env['balance.economyc.report'].create({
				'balance_economico_ids':data_balance,
				'property_mov_id':pd.id,
				})
				




class Balance_ecomonico(models.Model):	

	_name="balance.economyc.report.lines"

	
	##id relaccion
	property_mov_id = fields.Many2one(
	    'account.asset.asset',
	    string='Propiedad',
	)

	date_mov = fields.Date(
	    string='Fecha de movimiento',
	)

	type_mov = fields.Selection([
		('outbound', "Enviar dinero"), 
		('inbound', "Recibe dinero"),
		('transfer',"Transferencia Interna")])


	type_payment = fields.Selection([('r', "Renta"), 
		("m", "Mantenimiento"), ("s", "Servicio"), ("o", "Otros")])

	cant_mov = fields.Float(string='Cantidad')

	acum_mov = fields.Float(string='Acumulado')

	decription_mov = fields.Char(string='Descripcion')

	payment_mov_id = fields.Many2one('account.payment',
	    string='Pago')


	company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.user.company_id)

	currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        string='Currency',
        required=True)

	line_invoice = fields.Text(
	    string='Desarrollo de pago',
	)

	balance_economyc_lines_id = fields.Many2one(
	    'balance.economyc.report',
	    string='Balance economico lines',
	)

