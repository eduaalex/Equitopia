# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response,request
from odoo.exceptions import UserError
import json

class Website_dashborad_property(http.Controller):
	@http.route(['/my_properties'], type='http', auth="user", website=True)
	def my_properties_http(self, **post):
		vals = {}
		usuario=request.env['res.users'].sudo().search([
			('id','=',http.request.env.context.get('uid'))]).partner_id.id

		mantimientos=request.env['maintenance.request'].search([('property_id','=',usuario)])
		contratos=request.env['account.analytic.account']
		contratos_15dia_menos=[]
		contratos_16_30_dias=[]
		contratos_31_60_dias=[]
		contratos_mas_60_dias=[]

		for index_contrato in contratos:
			dias_restantes=index_contrato.date-index_contrato.date_start
			if dias_restantes<15:
				contratos_15dia_menos.append(index_contrato)
			if dias_restantes>15 and dias_restantes<=30:
				contratos_16_30_dias.append(index_contrato)
			if dias_restantes>31 and dias_restantes<=60:
				contratos_31_60_dias.append(index_contrato)
			if dias_restantes>60:
				contratos_mas_60_dias.append(index_contrato)




		vals.update({
			'todos_mantenimientos':mantimientos,
		})
		return request.render("website_custom_property.my_properties_onload", vals)


