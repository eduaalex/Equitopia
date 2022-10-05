# -*- coding: utf-8 -*-
from curses.ascii import US
from logging.config import valid_ident
from multiprocessing import managers
from re import U
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

	@http.route(['/my_properties'], type='http', auth="user", website=True)
	def my_properties_http(self, **post):
		vals = {}
		locale.setlocale( locale.LC_ALL, '' )
		#buscar propiedades del usuario
		propidades=request.env['account.asset.asset'].sudo().search(
			[('property_owner','=',self.get_user_login())])
		#todos los contratos
		contratos=request.env['account.analytic.account'].sudo().search(
			[('property_owner_id','=',self.get_user_login())])
		
		mantimientos=request.env['maintenance.request'].sudo().search([])
		count_contratos_15dia_menos=0
		count_contratos_16_30_dias=0
		count_contratos_31_60_dias=0
		count_contratos_mas_60_dias=0
		fecha_actual=date.today()
		for index_contrato in contratos:
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_15=15
			dias_30=30
			dias_31=31
			dias_60=60
			if dias_restantes < dias_15:
				count_contratos_15dia_menos+=1				
			if dias_restantes >= dias_15 and dias_restantes <= dias_30:
				count_contratos_16_30_dias+=1
			if dias_restantes >= dias_31 and dias_restantes <= dias_60:
				count_contratos_31_60_dias+=1
			if dias_restantes > dias_60:
				count_contratos_mas_60_dias+=1
		
		list_manenimientos=[]
		for mane in mantimientos:
			if mane.property_id.property_owner.id==self.get_user_login():
				list_manenimientos.append(mane)

		data_payment={}
		pagos_data=[]
		suma_per_amount=0.0
		suma_espera=0.0
		#recorrer propiedades
		for property_tenant in propidades:
			contratos=request.env['account.analytic.account'].sudo().search([('property_id','=',property_tenant.id)])
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
				'estado':property_tenant.state,				
				'propiedad':property_tenant.name,
				'suma_debe':str(locale.currency(amount,grouping=True)),
				'suma_haber':str(locale.currency(esperda,grouping=True)),
			}
			pagos_data.append(data_payment)	
	
		
		vals.update({
			'todos_propidades':pagos_data,
			'cantidad_contratos_15dia_menos':count_contratos_15dia_menos,
			'cantidad_contratos_16_30_dias':count_contratos_16_30_dias,
			'cantidad_contratos_31_60_dias':count_contratos_31_60_dias,
			'cantidad_contratos_mas_60_dias':count_contratos_mas_60_dias,
			'list_manenimientos':list_manenimientos,
			'suma_per_amount':str(locale.currency(suma_per_amount,grouping=True)),
			'suma_espera':str(locale.currency(suma_espera,grouping=True)),


		})
		return request.render("website_custom_property.my_properties_onload", vals)
	
	@http.route(['/rango_menos_15'], type='http', auth="user", website=True)
	def my_teancy_rango_menos_15_http(self, **post):
		vals = {}
		contratos=request.env['account.analytic.account'].sudo().search(
			[('property_owner_id','=',self.get_user_login())])
		contratos_15dia_menos=[]
		fecha_actual=date.today()
		for index_contrato in contratos:
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_15=15
			if dias_restantes < dias_15:
				contratos_15dia_menos.append(index_contrato)
		
		vals.update({
			'lista_contatos':contratos_15dia_menos,
			'titulo':"Vence en 15 días o menos"
		})
		return request.render("website_custom_property.my_properties_tenancy", vals)

	

	@http.route(['/rango_16_30'], type='http', auth="user", website=True)
	def my_teancy_rango_16_30_http(self, **post):
		vals={}
		contratos=request.env['account.analytic.account'].sudo().search(
			[('property_owner_id','=',self.get_user_login())])
		contratos_16_30_dias=[]
		fecha_actual=date.today()
		for index_contrato in contratos:
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_15=15
			dias_30=30
			if dias_restantes >= dias_15 and dias_restantes <= dias_30:
				contratos_16_30_dias.append(index_contrato)
		vals.update({
			'lista_contatos':contratos_16_30_dias,
		    'titulo':"Vence en 16-30 días"
		})
		return request.render("website_custom_property.my_properties_tenancy", vals)

	@http.route(['/rango_31_60'], type='http', auth="user", website=True)
	def my_teancy_rango_31_60_http(self, **post):
		vals={}
		contratos=request.env['account.analytic.account'].sudo().search(
			[('property_owner_id','=',self.get_user_login())])
		contratos_31_60_dias=[]
		fecha_actual=date.today()
		for index_contrato in contratos:
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_31=31
			dias_60=60
			if dias_restantes >= dias_31 and dias_restantes <= dias_60:
				contratos_31_60_dias.append(index_contrato)
		vals.update({
			'lista_contatos':contratos_31_60_dias,
			'titulo':"Vence en 31-61 días"
		})
		return request.render("website_custom_property.my_properties_tenancy", vals)

	@http.route(['/rango_mas_60'], type='http', auth="user", website=True)
	def my_teancy_rango_mas_60_http(self, **post):
		vals={}
		contratos=request.env['account.analytic.account'].sudo().search(
			[('property_owner_id','=',self.get_user_login())])
		contratos_mas_60_dias=[]
		fecha_actual=date.today()
		for index_contrato in contratos:
			dias_restantes=(index_contrato.date-fecha_actual).days
			dias_60=60
			if dias_restantes >= dias_60:
				contratos_mas_60_dias.append(index_contrato)
	
		vals.update({
			'lista_contatos':contratos_mas_60_dias,
			'titulo':"Vence en más de 60 días"
		})
		return request.render("website_custom_property.my_properties_tenancy", vals)
	@http.route(['/property_details'], type='http', auth="user", website=True)
	def property_details_http(self, **kw):
		vals={}
		propiedad=request.env['account.asset.asset'].sudo().search([('id','=',kw.get('propiedad_evaluar'))])
		vals.update({
			'propiedad':propiedad,
		})
		return request.render("website_custom_property.properties_details",vals)

	@http.route(['/maintenance_details'], type='http', auth="user", website=True)
	def maintenance_details_http(self, **kw):		
		vals={}
		manteni=request.env['maintenance.request'].sudo().search([('id','=',kw.get('mantenimiento'))])
		vals.update({
			'manteni':manteni,
		})

		return request.render("website_custom_property.maintenance_details", vals)

	@http.route(['/tenant_details'], type='http', auth="user", website=True)
	def tenant_details_http(self, **kw):		
		vals={}
		contrato=request.env['account.analytic.account'].sudo().search([('id','=',kw.get('contrato'))])
		vals.update({
			'contrato':contrato,
		})

		return request.render("website_custom_property.tenant_details", vals)


	@http.route(['/clock_alert'], type='http', auth="user", website=True)
	def clock_alert_http(self, **kw):	
		vals={}
		alertadeusuario=request.env['alert.clock'].sudo().search([('duenos_id','=',self.get_user_login())])
		vals.update({
		 'alerta':alertadeusuario, 
		})
		return request.render("website_custom_property.alert_clock",vals)
	
	@http.route(['/clock_alert_count'], type='json', auth="user", website=True)
	def clock_alert_count(self,**kw):
		alert_count=request.env['alert.clock'].sudo().search_count([('duenos_id','=',self.get_user_login())])
		result={
			'count_alert':alert_count
		}
		return result
	




