var input=$("#calendary_data").val()

function search_evento(data,id){
  for(let item of data){
      if(item['id']==id){
          var dt=[item['id'],item['title'],item['start'],item['end'],item['descripcion']
          ,item['propiedad'],item['contract_id']]
          return dt
      }
    }
} 

if(typeof(input) !=='undefined'){
   var calendarEl = document.getElementById('fullcalendar_property');

   $.get('/calendario/eventos',function(data){
      var calendar = new FullCalendar.Calendar(calendarEl, {
          headerToolbar: {
            left: 'prev,next,today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        locale:'es',
        editable: true,
        events:data,
        eventClick:function(info){
        var event=search_evento(data,info.event.id)
        $("#titleModalLabel").text(info.event.title)    
        $("#item_evento").val(info.event.title)    
        $("#item_fecha_inicio").val(event[2]) 
        $("#item_fecha_fin").val(event[3])
        if(event[4]!=false){
          $("#item_descrip").val(event[4])  
        }        
        $("#item_propiedad").val(event[5])
        var link='/tenant_details?contrato='+event[6]        
        $("#item_mas").attr('href',link)
        $("#modalcalendario").modal()
        },
      });     

    calendar.render();
   });
  
}

