$('input[name="dates"]').daterangepicker({
    startDate:moment().startOf('month'),
    endDate:moment().endOf('month'),
    ranges: {
        'Hoy': [moment(), moment()],
        'Ayer': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
        'Ultimos 7 Días': [moment().subtract(6, 'days'), moment()],
        'Ultimos 30 Días': [moment().subtract(29, 'days'), moment()],
        'Este Mes': [moment().startOf('month'), moment().endOf('month')],
        'Ultimo Mes': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
     }
});


