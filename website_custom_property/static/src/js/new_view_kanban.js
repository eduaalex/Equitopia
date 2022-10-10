$.get('/load/kanban_title',function(data){
    $("#titles").val(JSON.stringify(data))  

});
function generarLetra(){
	var letras = ["a","b","c","d","e","f","0","1","2","3","4","5","6","7","8","9"];
	var numero = (Math.random()*15).toFixed(0);
	return letras[numero];
}
function colorHEX(){
	var coolor = "";
	for(var i=0;i<6;i++){
		coolor = coolor + generarLetra() ;
	}
	return "#" + coolor;
}
$.get('/load/kanban_data/',function(data){
   
   var titles=$("#titles").val()
   var titulos=[];
   var titulos_color=[]
   if(typeof(titles) !=='undefined'){
      for(var item of JSON.parse(titles)){
         titulos.push(item['title'])
         titulos_color.push(colorHEX())
      }  
      $('#kanban').kanban({
         titles: titulos,
         items: data,
         colours: titulos_color,
       });    
   }  

})
