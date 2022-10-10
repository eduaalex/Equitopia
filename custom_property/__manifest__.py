{
    'name': 'Custom Property',
    'version': '13.0.1.0.0',
    'category': 'Wb',
    'summary': """
            custom property:
            
     """,
    'author': '',
    'license': 'LGPL-3',
    'website': '',
    'depends': [
       'property_management',
       'property_landlord_management',
       'om_account_asset',
       'calendar',
    ],
    'data': [
       'security/ir.model.access.csv',
       'views/view_property_for_user.xml',
       'views/count_pago_view.xml',
       'views/Rent_type_view.xml',
       'views/calendary_property.xml',
       'report/report_contrator_email.xml',
       'report/menu_report_contraro.xml',
       'report/report_invoice_pago.xml',
       'data/email_template.xml',
    ],
   
}
