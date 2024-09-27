var tipo = getUrlVars()["tipo"];

function getUrlVars() {

    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi,
        function(m, key, value) {
            vars[key] = value;
        });
    return vars;
}


function getDateValue(fecha) {
    return (fecha.getMonth() + 1) + "/1" + "/" + fecha.getFullYear();
}

function format(valor, contenedor) {
    var resultado = "";
    var separador = ","; // separador para los miles
    var sepDecimal = '.'; // separador para los decimales
    var splitStr = valor.split('.');
    var splitLeft = splitStr[0];
    var splitRight = splitStr[1];
    if (splitLeft == '' || splitLeft == 'undefined' || splitLeft == null) {
        splitLeft = '0';
    };
    if (splitRight == '' || splitRight == 'undefined' || splitRight == null) {
        splitRight = '00';
    };

    var resultado = (splitLeft.toString().replaceAll('´', '')).replace(/\B(?=(\d{3})+(?!\d))/g, ",");

    jQuery(contenedor).val(resultado + sepDecimal + splitRight.replaceAll('´', ''));
};



function numberValidator(event, withPoint = true) {
    let patron = withPoint ? /[0-9.]/ : /[0-9]/;
    let allowedSpecialKeys = [8, 9, 13, 37, 38, 39, 40];
    let key = event.key;
    if (patron.test(key) || allowedSpecialKeys.includes(event.keyCode)) {
        return true;
    } else {
        return false;
    }
}