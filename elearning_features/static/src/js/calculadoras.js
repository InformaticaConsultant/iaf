jQuery(document).ready(function() {
    //Generic
    let showGlosario = true;
    jQuery('.aside.calculator .terminos .glosario-title img').on('click', () => {
        let transformValue = showGlosario ? 'rotate(180deg)' : 'rotate(0deg)';
        jQuery('.aside.calculator .terminos ul').fadeToggle();
        jQuery('.aside.calculator .terminos .glosario-title img').css('transform', transformValue);
        showGlosario = !showGlosario;
    })

    // Calculadora de Prestamos Personales
    // Toggle pagos extraordinarios y reusmen detallado
    let extraordIsHide = true;
    jQuery('#extraordinarios').on('click', (event) => {
        if (event.target.id == 'extraordinarios' || event.target.nodeName == "H3") {
            let transformValue = extraordIsHide ? 'rotate(180deg)' : 'rotate(0deg)';
            jQuery("main .extraordinarios table").fadeToggle();
            jQuery("main .extraordinarios .chevron").css("transform", transformValue);
            extraordIsHide = !extraordIsHide;
        }
    });
    jQuery("main .extraordinarios .chevron").on("click", function() {
        let transformValue = extraordIsHide ? 'rotate(180deg)' : 'rotate(0deg)';
        jQuery("main .extraordinarios table").fadeToggle();
        jQuery("main .extraordinarios .chevron").css("transform", transformValue);
        extraordIsHide = !extraordIsHide;
    });
    let detalladoIsHide = true;
    jQuery('#detallado').on('click', (event) => {
        if (event.target.id == 'detallado' || event.target.nodeName == "H3") {
            let transformValue = detalladoIsHide ? 'rotate(180deg)' : 'rotate(0deg)';
            jQuery("main .detallado table").fadeToggle();
            jQuery("main .detallado .chevron").css("transform", transformValue);
            detalladoIsHide = !detalladoIsHide;
        }
    });
    jQuery("main .detallado .chevron").on("click", function() {
        let transformValue = detalladoIsHide ? 'rotate(180deg)' : 'rotate(0deg)';
        jQuery("main .detallado table").fadeToggle();
        jQuery("main .detallado .chevron").css("transform", transformValue);
        detalladoIsHide = !detalladoIsHide;
    });


    // jQuery("#categoria").val("Préstamos personales");


    jQuery("#categoria").on("change", function(env) {
        let option = jQuery("#categoria").val();


        switch (option) {
            case "Préstamos personales":
                window.location.href = "/calculadora-prestamos-personales";
                break;
            case "Inversión":
                window.location.href = "/calculadora-certificado-inversion";
                break;
            case "Fondos de emergencia":
                window.location.href = "/calculadora-fondo-de-emergencias";
                break;

            case "Meta de ahorro":
                window.location.href = "/calculadora-de-ahorro";
                break;

            case "Plan de retiro":
                window.location.href = "/calculadora-de-pension";
                break;
        }


    });

});