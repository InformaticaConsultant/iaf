console.log("Loading Custom JS");

if($('html').attr('lang')=='es-DO'){
    $('form').validate({
        messages: {
            email:  "tu correo"
        }
    });
}else{
    $('form').validate({
        messages: {
            email:  "No hablamos gringo.. Tu correo"
        }
    });
};
