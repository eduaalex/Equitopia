{
    'name': 'Website Custom dashboard Property',
    'version': '13.0.1.0.0',
    'category': 'Website',
    'summary': """
            custom dashboard property:
            
     """,
    'author': '',
    'license': 'LGPL-3',
    'website': '',
    'depends': [
       'property_management',
       'property_landlord_management',
       'om_account_asset',
    ],
    'data': [
       'security/ir.model.access.csv',
       'views/website_template.xml', 
       'views/website_dashboard.xml',
       'views/my_property.xml',
       'views/propietario_calendario.xml',
       'views/website_views_tenant_tenancy.xml',
       'views/website_views_property_details.xml',
       'views/website_views_maintenance_details.xml',
       'views/Website_alert_clock.xml',
       'views/alert_clock.xml',
       'views/website_views_tenant_details.xml',

       
    ],
   
}
