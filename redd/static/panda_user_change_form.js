function S4() {
   return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
}

function guid() {
   return (S4()+S4()+S4()+S4()+S4()+S4()+S4()+S4()+S4()+S4());
}

django.jQuery(document).ready(function() {
    django.jQuery("#id_api_key-__prefix__-key").val(guid())    
});
