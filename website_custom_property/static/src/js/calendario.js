odoo.define('website_custom_propery_calendary',function(require){
  'use strict'

var ajax = require('web.ajax');
var rpc = require('web.rpc');   

$(document).on('click','#item_mas',function(){
 var programado=$('#item_progamado').val() 
 var recibido=$('#item_recibido').val()
 var propiedad=$('#item_propiedad').val()
 var fecha_mes_ano=$("#item_fecha_inicio").val()
 var id=$("#item_id").val() 


 ajax.jsonRpc("/calendary/paymentoutin","call",{
  'programado':programado,
  'recibido':recibido,
  'propiedad':propiedad,
  'fecha':fecha_mes_ano,
  'id':id,
 }); 

 });

function next_prev(){
 var fecha_search=$("#fecha_search").val()
 var lista_id=[];
  $('.item_check').each(function(){
      if ($(this).is(":checked")){
        lista_id.push($(this).attr('id'))
      }
  });
 
 ajax.jsonRpc('/loadata/propiedad','call',{
  'fecha_ano_mes_cuerr':fecha_search,
  'propiedades':lista_id,
 }).then(function(data){
  console.log(data)
  $("#data_propiedad").html(data['html'])
 }); 
} 



$(document).on('click','#siguiente',function(){
  next_prev();
});

$(document).on('click','#atraz',function(){
  next_prev();
});


});

var input=$("#calendary_data").val()
function search_evento(data,id){
  for(let item of data){
      if(item['id']==id){
          var dt=[item['id'],item['title'],item['start'],item['end'],item['descripcion']
          ,item['propiedad'],item['contract_id'],item['programado'],item['recibido']]
          return dt
      }
    }
} 

 var calendarEl = document.getElementById('fullcalendar_property');
 var calendar=null;
 
 function set_mes_actual(calendar){
  var mes_curre=calendar.currentData.currentDate.getUTCMonth()+1
  var ano_curre=calendar.currentData.currentDate.getFullYear()
  var anomes=mes_curre+"/"+ano_curre
  $("#fecha_search").val(anomes)
 }
   
if(typeof(input) !=='undefined'){
  calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar:{
            left: 'prev,next',
            center: 'title',
            right: 'dayGridMonth'
        },    
        locale:'es',               
      }); 
   calendar.render();
 }

$(document).on('change','#property_search',function(){  
    var lista_id=[];
    $('.item_check').each(function(){
      if ($(this).is(":checked")){
        lista_id.push($(this).attr('id'))
      }
    });

    $.get('/calendario/eventos',function(data){
      let array=[];
      var html=''
      var totalprogramado=0.0,totalrecibido=0.0
      for(let item of lista_id){     
        var total_programado=0.0,total_recibido=0.0,propiedad=null,color=null   
        for(let itera of data.filter(e => e.idpropieda==item)){
          array.push(itera);
          total_programado+=itera['programado_op']
          total_recibido+=itera['recibido_op']
          propiedad=itera['propiedad']
          color=itera['color']
        }  
       
        html+="<div class='card'>"
        html+="<strong>Propiedad:</strong>"+propiedad+"<br/>"
        html+="<strong>Programado:</strong> <span class='tpro'>"+total_programado+"</span>"
        html+="<strong>Recibido:</strong> <span class='trecb'>"+total_recibido+"</span>"         
        html+="</div><br/>" 
        totalprogramado+=total_programado
        totalrecibido+=total_recibido        
      }

        html+="<div class='card'>"
        html+="<strong>Total:</strong><br/>"
        html+="<strong>Programado:</strong> <span class='tpro'>"+totalprogramado+"</span>"
        html+="<strong>Recibido:</strong> <span class='trecb'>"+totalrecibido+"</span>"         
        html+="</div><br/>"   
     
      $("#data_propiedad").html(html)

      calendar = new FullCalendar.Calendar(calendarEl, {   
        headerToolbar: {
            left: 'prev,next',
            center: 'title',
            right: 'dayGridMonth'
        },
        locale:'es',
        editable: true,
        events:array,
        eventClick:function(info){
        var event=search_evento(data,info.event.id);
        $("#titleModalLabel").text(info.event.title);
        var start=new Date(event[2].replace('T',' '));        
        var stop=new Date(event[3].replace('T',' '));
        var datestart=start.getDate()+"/"+(start.getMonth()+1)+"/"+start.getFullYear()+" "+
        start.getHours()+":"+start.getMinutes();
        var datestop=stop.getDate()+"/"+(stop.getMonth()+1)+"/"+stop.getFullYear()+" "+
        stop.getHours()+":"+stop.getMinutes();
        $("#item_evento").val(info.event.title);    
        $("#item_fecha_inicio").val(datestart); 
        $("#item_fecha_fin").val(datestop);
        $("#item_progamado").val(event[7]);
        $("#item_recibido").val(event[8]);
        $("#item_id").val(event[0]);
        if(event[4]!=false){
          $("#item_descrip").val(event[4]);  
        }        
        $("#item_propiedad").val(event[5]);
        var link='/tenant_details?contrato='+event[6];        
        $("#item_mas").attr('href',link);
        $("#modalcalendario").modal();
        },
      });    

    calendar.render();      
   });
    //sumatiria total
    // console.log("---------2")
    // $('.tpro').each(function(){
    //  console.log($(this).val());
    // });
    // $('.trecb').each(function(){
    //   console.log($(this).val());
    // });

    //$("total_total")
});
//Al precionar los botones de next y prev 
 $(document).on('click','.fc-next-button',function(){
     set_mes_actual(calendar);
     $("#atraz").click();
 });
 $(document).on('click','.fc-prev-button',function(){
   set_mes_actual(calendar); 
   $("#siguiente").click();
 })  



