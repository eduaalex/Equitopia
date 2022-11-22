odoo.define('website_custom_property.custom_property_dashbord', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    
    
    function load_alert(){
        ajax.jsonRpc("/clock_alert_count",'call',{
        }).then(function(data){
            $("#clock_alert_count").text(data['count_alert']);
            
        });
    }

    var loggin=$("#users").val()
    
    if (typeof loggin !== "undefined"){
        setInterval(load_alert,3000);       
     
    $(".marca").each(function(index,element){
   if($(this).attr('checked')){
    $(this).closest('tr').css('font-weight','normal')
   }
   });

    

          
    $(document).on('click','#alertas,#marcar_leido',function(){
    var dicontrato=$(this).closest('tr').find('#idcontrato').text()
    ajax.jsonRpc("/alert/check",'call',{
        'dicontrato':dicontrato
        }).then(function(data){             
         location.reload();          
            
        });   
    });
    //Sacar mes actual
    const fecha=new Date();
    const mes=fecha.getMonth()+1;
    const ano=fecha.getFullYear();
    $("#buscardeano").val(ano);
    $("#select_meses").val(mes)

    load_property_data(ano,mes,-1);
       
    //cuando solo se use el filtro normal
    $(document).on('change','#select_meses,#propiead_haber,#buscardeano',function(){
        let mes_selecionado=$("#select_meses option:selected").val();
        let ano_selecionado=$("#buscardeano").val()
        let filtro=$("#propiead_haber option:selected").attr('id')
        $("#grafica_porcentajes_view").remove();
        $("#show_informacion_mensual").remove();
        $("#grafica_barras_view").remove();  
        $("#show_informacion_history").remove();     
        load_property_data(ano_selecionado,mes_selecionado,filtro);  
      
    })
    function load_property_data(ano,mes,filter_property){
       
       ajax.jsonRpc('/my_properties/info','call',{
            'ano':ano,
            'mes':mes,
            'propiedad':filter_property,
        }).then(function(data){  
            
            var $grafica=null;
            var html=''
            var data_metricas=[]
            var programado=0.0,total_recibido=0.0,tempgeneralpediente=0.0;
            for(let item of data['data']){                
                var imgsrc='data:image/png;base64,' + item['imagen'];
                html+="<tr>"
                html+="<td>"
                html+="<strong>Propiedad:</strong><span>"+item['propiedad']+"</span><br/>"
                html+="<img src='"+imgsrc+"' height='150px' width='150px' alt='No fotografia'/><br/>"
                html+="<span><strong>Estado:</strong>"+item['estado']+"</span>"
                html+="</td>"                
                html+="<td>"
                html+="<input type='hidden' class='propiedad_id' id='"+item['propiedad']+
                "' value='"+item['propiedad_id']+"'/>"
                html+="<canvas class='graficas_v2'  id='graficav2"+item['propiedad_id']+"'></canvas><br/>"
                html+="</td>"
                html+="<td>"
                html+="<canvas class='graficas_dinamicas'  id='grafica_porcentajes_view"+item['propiedad_id']+"'></canvas><br/>"
                html+="</td>"  
                html+="<td> <div class='calendar_dinamico' id='calendar"+item['propiedad_id']+"'></div></td>"
                html+="<td>"
                var metricas=item['metricas'];
                html+="<strong>Ingresos Netos:</strong><span class='metrica_in' id='ing_neto"+item['propiedad_id']+"' >"+convert(metricas[0])+"</span></br>"
                html+="<strong>HOA:</strong><span class='metrica_hoa' id='hoa"+item['propiedad_id']+"'>"+convert(metricas[1])+"</span></br>"
                html+="<strong>Otros gastos:</strong><span class='metrica_og' id='otros"+item['propiedad_id']+"'>"+convert(metricas[2])+"</span></br>"
                html+="<canvas class='graficarmetricas'  id='graficarmetricas"+item['propiedad_id']+"'></canvas><br/>"               
                html+="</td>"
                html+="</tr>"
                data_metricas.push([metricas[0],metricas[1],metricas[2]])   
                tempgeneralpediente=item['general_pediente']
                programado+=tempgeneralpediente[0][0]
                total_recibido+=tempgeneralpediente[0][1]

     
             }
            $("#table_result").html(html);
            $("#total_recibido").text(convert(total_recibido));
            $("#programado").text(convert(programado));
            $("#input_total_recibido").val(total_recibido);
            $("#input_programado").val(programado);


            
            //grafica dinamica 1-----------------------------------------------------------------
            var data_info=[]
            for(let item of data['data']){               
               data_info.push(item['use_property'][0])
            }
            var index=0;          
            $(".graficas_dinamicas").each(function(){//recorrer todo los canvas
               const element=$(this).attr('id');             
               graficas_dinamicas(element,data_info[index]);
               index+=1               

           }); 

           //calendario dinamico-------------------------------------------------------------------  
           var pro_pied=[]
           for(let item of data['data']){               
               pro_pied.push(item['propiedad_id'])
            }
            var index=0
           $(".calendar_dinamico").each(function(){//recorrer todo los div
               const element=$(this).attr('id'); 
               calendario_dinamico(element,pro_pied[index]);
               index+=1               

           });
           
           //grafica dinamica 2--------------------------------------------------------------------
            var datainfo=[]
            for(let item of data['data']){
               const temp=item['general_pediente'][0]
               datainfo.push(temp);
            }
            var index=0;          
            $(".graficas_v2").each(function(){//recorrer todo los canvas
              const element=$(this).attr('id');   
             grafica_efectivo_programdo(element,datainfo[index]);
              index+=1             

          }); 
           //grafica para metricas-----------------------------------------------------------------
           var index=0;
           $(".graficarmetricas").each(function(){//recorrer todo los canvas
              const element=$(this).attr('id');   
              graficaciondemetricas(element,data_metricas[index]);
              index+=1;    

          }); 

          Mensual_informacion_graficas();     
            

 
            //INICION DE GRAFICA DE OCUPACION
            function  graficas_dinamicas(grafica,data){

                const image = new Image();
                image.src="website_custom_property/static/src/img/equitopia2.jpeg"
                const plugin = {
                  id: 'custom_canvas_background_image',
                  beforeDraw: (chart) => {
                    if (image.complete) {
                      const ctx = chart.ctx;
                      const {top, left, width, height} = chart.chartArea;
                      const x = left + width / 2 - image.width / 2;
                      const y = top + height / 2 - image.height / 2;
                      ctx.drawImage(image, x, y);
                    } else {
                      image.onload = () => chart.draw();
                    }
                  }
            };
             var ctxgrafica_ciruclar=new Chart(grafica,{
                type:'doughnut',
                data:{
                    labels:['Libre','Ocupado'],
                    datasets:[{
                        labels:'Ocupacion',
                        data: data,
                        backgroundColor: ["#e8c3b9","#3cba9f"],
                        borderColor:["#3cba9f","#e8c3b9"],
                        borderWidth: 1,
                    }]                  
            
                },        
                options: {
                    responsive: true,
                    legend:{
                        display:false
                    },
                    plugins:{                        
                        datalabels:{
                            formatter: (value,context)=>{
                                let mes_selecionado=$("#select_meses option:selected").val();
                                let ano=$("#buscardeano").val();
                                let days=new Date(ano,mes_selecionado,0).getDate()
                                let porcet=(value*100)/days 
                                return porcet.toPrecision(4)+"% \n "+ value.toPrecision(4) +" Dias"                                
                                
                          },
                          font: {
                                weight: 'bold',
                                size: 12,
                                
                           }

                        },
                        tooltip:{
                            callbacks:{
                              label: function(tooltipitem,data){
                                var label=ctxgrafica_ciruclar.data.labels[tooltipitem.dataIndex]
                                var value=ctxgrafica_ciruclar.data.datasets[tooltipitem.datasetIndex].data[tooltipitem.dataIndex]
                                let mes_selecionado=$("#select_meses option:selected").val();
                                let ano=$("#buscardeano").val();
                                let days=new Date(ano,mes_selecionado,0).getDate()
                                let porcet=(value*100)/days     


                                return label + "\n\n"+porcet.toPrecision(4)+"% \n " 
                                      +value.toPrecision(4)+" Dias"                

                        
                              }
                            }
                          },

                    },
            },
            plugins:[ChartDataLabels],   

            });

            }
             //GRAFICA DE BARRAS DE FLUJO DE EFECTIVO
             const ingreso_cobrado=data['ingreso_cobrado']
             const etiquetas=data['etiqueta']
             $("#grafica_barras").append("<canvas  id='grafica_barras_view' width='100%' height='100%'></canvas>")
             var $grafica_barras=null;
             if($("#grafica_barras").length!=0){
                $grafica_barras = document.querySelector("#grafica_barras_view")//.getContext('2d');
             }             
             $("#grafica_barras").css('width','95%').css('height','300px')
             var arry_data=[]
             var leng=ingreso_cobrado.length

             for(let i =0;i<leng;i++){
                arry_data.push({
                    label:etiquetas[i],
                    data:ingreso_cobrado[i],
                    backgroundColor: fondocolorRGB(),
                    borderColor:colorcolorRGB(),
                    hidden:true,
                    borderWidth: 1,
                    maxBarThickness:8,

                })
             }          
         
             var ctxgrafica_barras=new Chart($grafica_barras,{
                type:'bar',
                data:{
                    labels:['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre'
                        ,'Octubre','Noviembre','Diciembre'],
                    datasets:arry_data                  
            
                }, 
                options:{
                    maintainAspectRatio:false,
                    scales: {
                        xAxes: [{
                            barThickness: 6,
                            maxBarThickness: 8,
                        }]
                    },
                    legend:{
                            labels:{
                                font:{
                                    size: 14
                                }
                            },
                            title: {
                                display: true,
                                text: 'Flujo de efectivo'
                            }
                        },
                        plugins:{                        
                        datalabels:{
                            formatter: (value,context)=>{
                                if(value>0){
                                  return "Ingresos \n"+ convert(value);    
                                }
                                else{
                                    return ''
                                }
                                                                
                                
                          },
                          font: {
                                weight: 'bold',
                                size: 12,
                                
                           }

                        },
                        tooltip:{
                            callbacks:{
                             label: function(tooltipitem,data){
                                 var label=ctxgrafica_barras.data.labels[tooltipitem.dataIndex]
                                 var value=ctxgrafica_barras.data.datasets[tooltipitem.datasetIndex].data[tooltipitem.dataIndex]
                                 return label +"Ingresos \n"+convert(value)                 

                        
                               }
                            }
                          },

                    },
                },
                plugins:[ChartDataLabels],   

              
           
            });            
            $("#global_mes_cobrado").text(convert(data['renta_global_cobrados']));
            $("#global_mes_pen_cobrado").text(convert(data['rentas_globla_pendientes']));
            $("#input_global_mes_cobrado").val(data['renta_global_cobrados']);
            $("#input_global_mes_pen_cobrado").val(data['rentas_globla_pendientes']);
            $("#porcent_cobrado").text(data['porcent_cobrado']);
            $("#porcent_pend_cobro").text(data['porcent_pend_cobro']);
            $("#porcent_efectivo").text(data['porcent_efectivo']);
            $("#procent_no_efectivo").text(data['procent_no_efectivo']);
             create_grafic_history();

        });  
    }


   //INFORMACION DATA PARA EL CALENDARIO
    $(document).ready(function(){        
        var cl=$("#calendary_data").val()    
        if(typeof(cl)  === "undefined") {        
        }
        else
        {        
        //ajax para cargar las propiedades por usuario
         //para despues mostarlas en calendario    

          ajax.jsonRpc('/load/property/calendary','call',{
             }).then(function(data){
                $("#property_search").html(data['load'])
             });
        }      
             

    });


     ajax.jsonRpc('/load/property/dashbord','call',{
      }).then(function(data){
        $("#propiead_haber").html(data['load'])
       });


     
 function calendario_dinamico(calendar,filtro) {
     
    //minicalendario
    ajax.jsonRpc('/minicalendario','call',{
        'propiedad':filtro,
    }).then(function(data){
      $("#"+calendar).MEC({
      from_monday: false,
         events: data['eventos']
      });
    }); 


 }

}


$(document).on('click',"#export_dashbord",function(){
var prtContent = document.getElementById("print_button");
var WinPrint = window.open('', '', 'left=0,top=0,width=800,height=900,toolbar=0,scrollbars=0,status=0');
WinPrint.document.write(prtContent.innerHTML);
WinPrint.document.close();
WinPrint.focus();
WinPrint.print();
WinPrint.close();
});

});











