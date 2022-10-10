# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response,request
from odoo.exceptions import UserError
import json
from datetime import date
import locale
class Website_dashborad_property(http.Controller):
    
	def get_user_login(self):
		#usuario que tiene la session iniciada
		usuario=request.env['res.users'].sudo().search([
			('id','=',http.request.env.context.get('uid'))]).partner_id.id
		#propietario
		propierario=request.env['landlord.partner'].sudo().search(
			[('parent_id','=',usuario)]
		).id		
		return propierario
	
	def get_count_contratos(self,contratos):
		count_contratos=[0,0,0,0]
		fecha_actual=date.today()
		dias_15=15
		dias_30=30
		dias_31=31
		dias_60=60
		for index in contratos:
			dias_restantes=(index.date-fecha_actual).days
			if dias_restantes < dias_15:
				count_contratos[0]=count_contratos[0]+1
			if dias_restantes >= dias_15 and dias_restantes <= dias_30:
				count_contratos[1]=count_contratos[1]+1
			if dias_restantes >= dias_31 and dias_restantes <= dias_60:
				count_contratos[2]=count_contratos[2]+1
			if dias_restantes > dias_60:
				count_contratos[3]=count_contratos[3]+1
		return count_contratos
	

	def get_contratos_inquilino(self):
		data=request.env['account.analytic.account'].sudo().search(
			[('property_owner_id','=',self.get_user_login()),
			('state','!=','cancelled'),
			('is_property','=',True)])
		return data
	def get_contratos_propietario(self):
		data=request.env['account.analytic.account'].sudo().search(
			[('property_owner_id','=',self.get_user_login()),
			('state','!=','cancelled'),
			('is_landlord_rent','=',True)])
		return data
	def get_dicc_status(self,estado):
		if estado=='new_draft':
			return 'Reserva abierta'
		if estado=='draft':
			return 'Disponible'
		if estado=='book':
			return 'Reservada'
		if estado=='normal':
			return 'En Arrendamiento'
		if estado=='close':
			return 'Rebaja'
		if estado=='sold':
			return 'Vendida'
		if estado=='open':
			return 'Correr'
		if estado=='cancel':
			return 'Cancelar'


	@http.route(['/my_properties'], type='http', auth="user", website=True)
	def my_properties_http(self, **post):
		vals = {}
		locale.setlocale(locale.LC_ALL, '')
		#buscar propiedades del usuario
		propidades=request.env['account.asset.asset'].sudo().search(
			[('property_owner','=',self.get_user_login())])
		#todos los contratos
		contratos_inquilinos=self.get_contratos_inquilino()
		contratos_propietario=self.get_contratos_propietario()

		data_payment={}
		pagos_data=[]
		suma_per_amount=0.0
		suma_espera=0.0
		#recorrer propiedades
		for property_tenant in propidades:
			contratos=request.env['account.analytic.account'].sudo().search(
				[('property_id','=',property_tenant.id),('state','=','open')])

			amount=0.0
			esperda=0.0
			for sumas_itme in contratos:
				#sumar pagado experado
				amount=sum(sumas_itme.rent_schedule_ids.mapped('amount'))
				suma_per_amount+=amount
				#sumar pagado real
				pen_amount=sum(sumas_itme.rent_schedule_ids.mapped('pen_amt'))				
				#diferencia y cantidad esperada
				esperda=amount-pen_amount
				suma_espera+=esperda
			data_payment={
				'evaluar':property_tenant.id, 
				'estado':self.get_dicc_status(property_tenant.state),				
				'propiedad':property_tenant.name,
				'suma_debe':str(locale.currency(amount,grouping=True)),
				'suma_haber':str(locale.currency(esperda,grouping=True)),
			}
			pagos_data.append(data_payment)	
	
		vals.update({
			'todos_propidades':pagos_data,
			'contratos_inquilinos':self.get_count_contratos(contratos_inquilinos),
			'contratos_propietario':self.get_count_contratos(contratos_propietario),
     		'suma_per_amount':str(locale.currency(suma_per_amount,grouping=True)),
			'suma_espera':str(locale.currency(suma_espera,grouping=True)),
		})
		return request.render("website_custom_property.my_properties_onload", vals)

	@http.route(['/rango_menos_15'], type='http', auth="user", website=True)
	def my_teancy_rango_menos_15_http(self, **post):
		vals = {}	
		contratos_inq_15dia_menos=[]
		contratos_pro_15dia_menos=[]
		fecha_actual=date.today()
		for index_contrato in self.get_contratos_inquilino():
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_15=15
			if dias_restantes < dias_15:
				contratos_inq_15dia_menos.append(index_contrato)

		for index_contrato in self.get_contratos_propietario():
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_15=15
			if dias_restantes < dias_15:
				contratos_pro_15dia_menos.append(index_contrato)
		
		vals.update({
			'lista_contatos_inq':contratos_inq_15dia_menos,
			'lista_contatos_pro':contratos_pro_15dia_menos,
			'titulo_inq':"Vence en 15 días o menos inquilinos",
			'titulo_pro':"Vence en 15 días o menos propietario",
		})
		return request.render("website_custom_property.my_properties_tenancy", vals)

	

	@http.route(['/rango_16_30'], type='http', auth="user", website=True)
	def my_teancy_rango_16_30_http(self, **post):
		vals={}
		contratos_inq_16_30_dias=[]
		contratos_pro_16_30_dias=[]
		fecha_actual=date.today()
		for index_contrato in self.get_contratos_inquilino():
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_15=15
			dias_30=30
			if dias_restantes >= dias_15 and dias_restantes <= dias_30:
				contratos_inq_16_30_dias.append(index_contrato)

		for index_contrato in self.get_contratos_propietario():
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_15=15
			dias_30=30
			if dias_restantes >= dias_15 and dias_restantes <= dias_30:
				contratos_pro_16_30_dias.append(index_contrato)		
		vals.update({
			'lista_contatos_inq':contratos_inq_16_30_dias,
			'lista_contatos_pro':contratos_pro_16_30_dias,
		    'titulo_inq':"Vence en 16-30 días inquilino",
			'titulo_pro':"Vence en 16-30 días propietario",
		})
		return request.render("website_custom_property.my_properties_tenancy", vals)

	@http.route(['/rango_31_60'], type='http', auth="user", website=True)
	def my_teancy_rango_31_60_http(self, **post):
		vals={}
		contratos_inq_31_60_dias=[]
		contratos_pro_31_60_dias=[]
		fecha_actual=date.today()
		for index_contrato in self.get_contratos_inquilino():
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_31=31
			dias_60=60
			if dias_restantes >= dias_31 and dias_restantes <= dias_60:
				contratos_inq_31_60_dias.append(index_contrato)

		for index_contrato in self.get_contratos_propietario():
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_31=31
			dias_60=60
			if dias_restantes >= dias_31 and dias_restantes <= dias_60:
				contratos_inq_31_60_dias.append(index_contrato)
		vals.update({
			'lista_contatos_inq':contratos_inq_31_60_dias,
			'lista_contatos_pro':contratos_pro_31_60_dias,
			'titulo_inq':"Vence en 31-61 días inquilinos",
			'titulo_pro':"Vence en 31-61 días propietario",
		})
		return request.render("website_custom_property.my_properties_tenancy", vals)

	@http.route(['/rango_mas_60'], type='http', auth="user", website=True)
	def my_teancy_rango_mas_60_http(self, **post):
		vals={}
		contratos_inq_mas_60_dias=[]
		contratos_pro_mas_60_dias=[]
		fecha_actual=date.today()
		for index_contrato in self.get_contratos_inquilino():
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_60=60
			if dias_restantes >= dias_60:
				contratos_inq_mas_60_dias.append(index_contrato)
		for index_contrato in self.get_contratos_propietario():
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_60=60
			if dias_restantes >= dias_60:
				contratos_pro_mas_60_dias.append(index_contrato)	
		vals.update({
			'lista_contatos_inq':contratos_inq_mas_60_dias,
			'lista_contatos_pro':contratos_pro_mas_60_dias,
			'titulo_inq':"Vence en más de 60 días inquilino",
			'titulo_pro':"Vence en más de 60 días propietario",
		})
		return request.render("website_custom_property.my_properties_tenancy", vals)
	@http.route(['/property_details'], type='http', auth="user", website=True)
	def property_details_http(self, **kw):
		vals={}
		propiedad=request.env['account.asset.asset'].sudo().search(
			[('id','=',kw.get('propiedad_evaluar'))])
		vals.update({
			'propiedad':propiedad,
		})
		return request.render("website_custom_property.properties_details",vals)

	@http.route(['/maintenance_details'], type='http', auth="user", website=True)
	def maintenance_details_http(self, **kw):		
		vals={}
		manteni=request.env['maintenance.request'].sudo().search([('id','=',kw.get('slug'))])
		vals.update({
			'manteni':manteni,
		})

		return request.render("website_custom_property.maintenance_details", vals)

	@http.route(['/tenant_details'], type='http', auth="user", website=True)
	def tenant_details_http(self, **kw):		
		vals={}
		contrato=request.env['account.analytic.account'].sudo().search(
			[('id','=',kw.get('contrato'))])
		vals.update({
			'contrato':contrato,
		})

		return request.render("website_custom_property.tenant_details", vals)


	@http.route(['/clock_alert'], type='http', auth="user", website=True)
	def clock_alert_http(self, **kw):	
		vals={}
		alertadeusuario=request.env['alert.clock'].sudo().search(
			[('duenos_id','=',self.get_user_login())])
		vals.update({
		 'alerta':alertadeusuario, 
		})
		return request.render("website_custom_property.alert_clock",vals)
	
	@http.route(['/clock_alert_count'], type='json', auth="user", website=True)
	def clock_alert_count(self,**kw):	
		alert_count=request.env['alert.clock'].sudo().search_count(
			[('duenos_id','=',self.get_user_login())])
		result={
			'count_alert':alert_count
		}
		return result
	
	@http.route(['/load/kanban_title'], type='http', auth="user", website=True)
	def load_title_kanban(self):
		kanban=request.env['maintenance.stage'].sudo().search([])
		json_kanban_titles=[]
		for item in kanban:
			json_kanban_titles.append({
				'title':item.name,
			})
		return Response(json.dumps(json_kanban_titles), 
		content_type='application/json;charset=utf-8',status=200)



	@http.route(['/load/kanban_data'], type='http', auth="user", website=True)
	def load_task_kanban(self,**kw):
		json_lista_kanban=[]
		kanban=request.env['maintenance.request'].sudo().search([])
		for itemx in kanban:
			if itemx.property_id.property_owner.id==self.get_user_login():
				json_lista_kanban.append({
					'id': itemx.id,
					'title': itemx.name,
					'block': itemx.stage_id.name,
					'link': '/maintenance_details?slug='+str(itemx.id),
                    'link_text': itemx.property_id.name,
					'footer': itemx.user_id.name,
					})
				
			
		return Response(json.dumps(json_lista_kanban), 
		content_type='application/json;charset=utf-8',status=200)
	
	#cargar datos para el calendario
	@http.route('/calendario/eventos',type='http',website=True,auth='user')
	def calendary_event_http(self,**kw):
		user_id=request.env['res.users'].sudo().search(
			[('id','=',http.request.env.context.get('uid'))]).partner_id.id
		datos_calendario=request.env['calendar.event'].sudo().search(
			[('partner_ids','in',user_id)])	
		eventos=[]
		for evento in datos_calendario:
			eventos.append({
				'id':evento.id,
				'title':evento.name,
				'start':evento.start_date.strftime("%Y-%m-%d"),
				'end':evento.stop_date.strftime("%Y-%m-%d"),
				'textColor':"#1DE9B6",
                'descripcion':evento.description,
                'usuario':user_id,
                'contract_id':evento.property_tanency.id,
                'propiedad':evento.property_calendary.name,             
				})
		return Response(json.dumps(eventos), 
		content_type='application/json;charset=utf-8',status=200)

	@http.route(['/propiedades/calendario'], type='http', auth="user", website=True)
	def property_calendary_http(self, **kw):		
		return request.render("website_custom_property.propretary_calendary_show_data", {})


