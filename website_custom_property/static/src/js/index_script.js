odoo.define('custom_property_clock_alert', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    function load_alert(){
        ajax.jsonRpc("/clock_alert_count",'call',{
        }).then(function(data){
            $("#clock_alert_count").text(data['count_alert']);
            
        });
    }

    setInterval(load_alert,30000)


});