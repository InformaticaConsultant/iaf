// let $ = jQuery;
$.noConflict();
var a = 0;
var b = 0;
var c = 0;
var d = 0;
var r = 0;
var r2 = 0;

function formatNumerico(valor) {
    var resultado = "";
    var separador = ","; // separador para los miles
    var sepDecimal = '.'; // separador para los decimales

    switch (valor) {
        case 'a':
            a = jQuery("#textUnoCertificado").val().replaceAll('´', '');
            var contenedor = '#textUnoCertificado';
            var QuitarComa = a.replace(',', '').replaceAll('´', '');
            a = QuitarComa;
            format(a, contenedor);
            break;
        case 'b':
            b = jQuery("#textDosCertificado").val().replaceAll('´', '');
            var contenedor = '#textDosCertificado';
            var QuitarComa = b.replace(',', '');
            b = QuitarComa;
            format(b, contenedor);
            break;
        case 'c':
            c = jQuery("#textTresCertificado").val().replaceAll('´', '');
            var contenedor = '#textTresCertificado';
            var QuitarComa = c.replace(',', '');
            c = QuitarComa;
            format(c, contenedor);
            break;
        case 'd':
            d = jQuery("#textCuatroCertificado").val().replaceAll('´', '');
            var contenedor = '#textCuatroCertificado';
            var QuitarComa = d.replace(',', '');
            d = QuitarComa;
            format(d, contenedor);
            break;
        case 'r':
            r = jQuery("#textResultadosCertificado").val().replaceAll('´', '');
            var contenedor = '#textResultadosCertificado';
            var QuitarComa = r.replace(',', '');
            r = QuitarComa;
            format(r, contenedor);
            break;
        case 'r2':
            r2 = jQuery("#textResultadosDosCertificado").val().replaceAll('´', '');
            var contenedor = '#textResultadosDosCertificado';
            var QuitarComa = r2.replace(',', '');
            r2 = QuitarComa;
            format(r2, contenedor);
            break;
    };

};

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

    jQuery(contenedor).val(resultado + sepDecimal + splitRight);
};



function numberValidator(event, withPoint = true) {
    let allowedSpecialKeys = [8, 9, 13, 37, 38, 39, 40];
    let patron = withPoint ? /[0-9.]/ : /[0-9]/;
    let key = event.key;
    if (patron.test(key) || allowedSpecialKeys.includes(event.keyCode)) {
        return true;
    } else {
        return false;
    }
}

function deboAhorrar() {
    if (a == '') {
        alert("El Monto a invertir debe ser mayor a cero");
    } else {
        if (b == '') {
            alert("El campo de Plazo (meses) debe ser mayor a cero");
        } else {
            if (c == '') {
                alert("El campo de Tasa debe ser mayor a cero");
            } else {
                var valorDosCalculado = (b * 30) / 360;
                var valorTresCalculado = c / 100;

                var sumaPotencia = 1 + valorTresCalculado;
                var potencia = Math.pow(sumaPotencia, valorDosCalculado);
                var resultado = (a * potencia) - a;
                var resultadoDos = (a * potencia);

                jQuery("#textResultadosDosCertificado").val(parseFloat(resultado).toFixed(2));
                jQuery("#textResultadosCertificado").val(parseFloat(resultadoDos).toFixed(2));

                formatNumerico('r');
                formatNumerico('r2');
            };
        };
    };
};




window.addEventListener("pageshow", () => {
    jQuery("#categoria").val("Inversión");
});