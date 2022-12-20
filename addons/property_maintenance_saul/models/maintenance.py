from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime

# For debug use only
from odoo.exceptions import UserError,ValidationError

class MaintenanceTeamModified(models.Model):
    _inherit = 'maintenance.team'

    partner_id = fields.Many2one('res.partner', string='Company')


class MaintenanceNames(models.Model):
    _name = 'maintenance.names'

    name = fields.Char(string='Nombre de mantenimiento')
    maintenances = fields.One2many('maintenance.request', inverse_name='name')


class MaintenanceCategory(models.Model):
    _name = 'maintenance.category'

    name = fields.Char(string='Nombre de la categoria')
    maintenances = fields.One2many('maintenance.request', inverse_name='name')


class MaintenanceProperty(models.Model):
    _name = 'maintenance.property'

    name = fields.Many2one('maintenance.names')
    team_id = fields.Many2one('maintenance.team', string="Equipo responsable")
    cost = fields.Float(string="Costo")
    frequency = fields.Selection([('once', 'Unico'), ('Daily', 'Diario'), ('Weekly', 'Semanal'), ('Monthly', 'Mensual'), ('semestre', 'Semestral'), ('Yearly', 'Anual')], default='once', string="Frecuencia")
    to_charge = fields.Selection([('tenant','Inquilino'),('landlord','Propietario'),('admin','Administrador')], string="A cuenta de quien")
    category = fields.Many2one('maintenance.category', string='Categoria')
    is_service = fields.Boolean(default=False, string='Es un servicio?')
    property_id = fields.Many2one('account.asset.asset')


class MaintenanceRequestInherit(models.Model):
    _inherit = 'maintenance.request'

    name = fields.Many2one('maintenance.names')
    team_id = fields.Many2one('maintenance.team', string="Equipo responsable")
    cost = fields.Float(string="Costo")
    frequency = fields.Selection([('once', 'Unico'), ('Daily', 'Diario'), ('Weekly', 'Semanal'), ('Monthly', 'Mensual'), ('semestre', 'Semestral'), ('Yearly', 'Anual')], default='once', string="Frecuencia")
    to_charge = fields.Selection([('tenant','Inquilino'),('landlord','Propietario'),('admin','Administrador')], string="A cuenta de quien")
    category = fields.Many2one('maintenance.category', string='Categoria')
    charge = fields.Boolean(string="Aplicar cargo")
    is_service = fields.Boolean(default=False, string='Es un servicio?')

    maintenance_contract_id= fields.Many2one('maintenance.contract')
    is_for_tenant = fields.Boolean(default=False)


class MaintenanceContract(models.Model):
    _name = 'maintenance.contract'

    name = fields.Many2one('maintenance.names')
    maintenance_requests = fields.One2many('maintenance.request', inverse_name='maintenance_contract_id')
    charge = fields.Boolean(string="Aplicar cargo")
    analytic_id = fields.Many2one('account.analytic.account')
    property_id = fields.Many2one('account.asset.asset')
    cost = fields.Float(string='Costo')
    team = fields.Many2one('maintenance.team', string='Equipo responsable') #,compute='_compute_team', )
    frequency = fields.Selection([('once', 'Unico'),('Daily', 'Diario'), ('Weekly', 'Semanal'), ('Monthly', 'Mensual'), ('Semestral', 'Semestral'), ('Yearly', 'Anual')], string="Frecuencia")
    category = fields.Many2one('maintenance.category', string='Categoria')
    schedule_date = fields.Datetime('Fecha programada', required=True)
    is_service = fields.Boolean(default=False, string='Es un servicio?')

    @api.onchange('team')
    def update_teams(self):
        for rec in self:
            for request in rec.maintenance_requests:
                request.team = rec.team.id


class AccountAnalyticModified(models.Model):
    _inherit = 'account.analytic.account'

    def _compute_frequency(self):
        for rec in self:
            date_diff = (rec.chech_out - rec.chech_in)
            if date_diff < datetime.timedelta(days=8):
                rec.frequency = 'Daily'
            elif date_diff < datetime.timedelta(days=32):
                rec.frequency = 'Weekly'
            elif date_diff < datetime.timedelta(days=30*6):
                rec.frequency = 'Monthly'
            elif date_diff < datetime.timedelta(days=365):
                rec.frequency = 'Semestral'
            else:
                rec.frequency = 'Yearly'

    def _compute_rent_payment(self):
        for rec in self:
            if len(rec.rent_schedule_ids) > 0:
                rec.rent_payment = rec.rent_schedule_ids[0]
            else:
                rec.rent_payment = False

    commission_value = fields.Float(string="Comisión")
    commission_percentage = fields.Float(string="Comisión (porcentaje)")
    maintenance_per_property = fields.One2many('maintenance.contract', inverse_name='analytic_id')
    frequency = fields.Selection([('Daily', 'Diario'), ('Weekly', 'Semanal'), ('Monthly', 'Mensual'), ('Semestral', 'Semestral'), ('Yearly', 'Anual')], compute='_compute_frequency', string="Frecuencia")
    # Mirror contract: For tenant view
    mirror_contract_id = fields.Many2one('account.analytic.account')
    # Mirror contract: For landlord view
    tenant_tenancy_id = fields.Many2one('account.analytic.account')
    rent_payment = fields.Many2one('tenancy.rent.schedule', compute="_compute_rent_payment")

    def open_payment(self):
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('account.view_move_form').id,
                'res_model': 'tenancy.rent.schedule',
                'res_id': self.rent_payment.id,
                'target': 'current',
                }

    def add_contract_maintenance(self, rec, maintenance):
        self.env['maintenance.contract'].create([{
            'name': maintenance.name.id,
            'frequency': maintenance.frequency,
            'analytic_id': rec.id,
            'property_id': rec.property_id.id,
            'schedule_date': rec.chech_in,
            'team': maintenance.team_id.id,
            'cost': maintenance.cost,
            'charge': True,
            'is_service': maintenance.is_service,
            }])

    def create_maintenance_request(self, rec, maintenance, times, times_factor, once=False):
        return self.env["maintenance.request"].create([{
            'name': maintenance.name.id,
            'maintenance_team_id': maintenance.team.id,
            'schedule_date': maintenance.schedule_date + times * times_factor if not once else rec.chech_out,
            'property_id': maintenance.property_id.id,
            'tenant_id': rec.tenant_id.id,
            'maintenance_contract_id': maintenance.id,
            'is_for_tenant': True,
            'is_service': maintenance.is_service,
            'cost': maintenance.cost,
            }])


    def load_maintenance_requests(self):
        for rec in self:
            if rec.is_landlord_rent:
                to_charge_query = 'landlord'
            else:
                to_charge_query = 'tenant'
            related_recordset = rec.property_id.maintenance_per_property.search(
                    [
                        ("to_charge", "=", to_charge_query),
                        ("property_id", "=", rec.property_id.id),
                        '|',
                        ("frequency", "=", rec.frequency),
                        ("frequency", "=", "once")
                        ]
                    )
            for maintenance in related_recordset:
                self.add_contract_maintenance(rec, maintenance)

            rec.maintenance_per_property = self.env['maintenance.contract'].search([('analytic_id', '=', rec.id)])

            for maintenance in rec.maintenance_per_property:
                times = datetime.timedelta(0)
                maintenance_requests = []
                if maintenance.frequency == 'Daily':
                    while times < rec.chech_out - rec.chech_in:
                        maintenance_requests.append(self.create_maintenance_request(rec, maintenance, times, 1))
                        times += datetime.timedelta(1)
                elif maintenance.frequency == 'Weekly':
                    while times < rec.chech_out - rec.chech_in:
                        maintenance_requests.append(self.create_maintenance_request(rec, maintenance, times, 8))
                        times += datetime.timedelta(1)
                elif maintenance.frequency == 'Monthly':
                    while times < rec.chech_out - rec.chech_in:
                        maintenance_requests.append(self.create_maintenance_request(rec, maintenance, times, 32))
                        times += datetime.timedelta(1)
                elif maintenance.frequency == 'Semestral':
                    while times < rec.chech_out - rec.chech_in:
                        maintenance_requests.append(self.create_maintenance_request(rec, maintenance, times, 30*6))
                        times += datetime.timedelta(1)
                elif maintenance.frequency == 'Yearly':
                    while times < rec.chech_out - rec.chech_in:
                        maintenance_requests.append(self.create_maintenance_request(rec, maintenance, times, 365))
                        times += datetime.timedelta(1)
                else:
                    maintenance_requests.append(self.create_maintenance_request(rec, maintenance, times, 1, once=True))
                maintenance.maintenance_requests = self.env['maintenance.request'].search([('maintenance_contract_id', '=', maintenance.id)]) 
                for maintenance_request in maintenance.maintenance_requests:
                    vard_data={
                            'start_date':maintenance_request.schedule_date,
                            'amount':maintenance_request.cost,
                            'pen_amt':maintenance_request.cost,
                            'property_id': rec.property_id.id,
                            'tenancy_id': rec.id,
                            'currency_id': rec.currency_id.id or False,
                            'rel_tenant_id': rec.tenant_id.id,									
                            'is_service': maintenance_request.is_service,
                            'maintenance_id': maintenance_request.id,
                            #'notes': maintenance_request.name.name,
                            }
                    rec.write({
                        'rent_schedule_ids':[(0,0,vard_data)]
                        })



    def create_mirror_contract(self):
        # Mirror contract
        for rec in self:
            if not rec.mirror_contract_id:
                new_mirror = {
                        'name': rec.name,
                        'code': 'LL/' + rec.code[2:],
                        'property_id': rec.property_id.id,
                        'property_owner_id': rec.property_id.property_owner.id,
                        'date_start': rec.date_start,
                        'date': rec.date,
                        'chech_in': rec.chech_in,
                        'chech_out': rec.chech_out,
                        'ten_date': rec.ten_date,
                        'frequency': rec.frequency,
                        'is_landlord_rent': True,
                        'tenant_tenancy_id': rec.id,
                        'landlord_rent': rec.landlord_rent,
                        'deposit': rec.deposit,
                        'tipo_tarifa': rec.tipo_tarifa,
                        }
                mirror_record = rec.mirror_contract_id.create([new_mirror,])
                rec.mirror_contract_id = mirror_record[0].id

    def calcular_precios_renta(self):
        res = super(AccountAnalyticModified,self).calcular_precios_renta()

        self.load_maintenance_requests()
        self.create_mirror_contract()
        self.mirror_contract_id.load_maintenance_requests()

        return res

    def propertary_tenant_start(self):
        self.load_maintenance_requests()
        self.action_invoice_payment()  # Generate maintenance invoices

class MaintenanceAsset(models.Model):
    _inherit = 'account.asset.asset'
    maintenance_per_property = fields.One2many(
            comodel_name='maintenance.property',
            inverse_name='property_id',
            store=True)

