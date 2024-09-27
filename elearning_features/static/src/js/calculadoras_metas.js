// let $ = jQuery;
$.noConflict();
var a = 0;
var b = 0;
var c = 0;
var d = 0;
var e = 0;
var r = 0;
var r2 = 0;

function formatNumerico(valor) {
    var resultado = "";
    var separador = ","; // separador para los miles
    var sepDecimal = '.'; // separador para los decimales

    switch (valor) {
        case 'a':
            a = document.querySelector("#meta_ahorro").value.replaceAll('´', '');
            var contenedor = '#meta_ahorro';
            var QuitarComa = a.replace(',', '');
            a = QuitarComa.replaceAll(/\.{2,}/g, '.');
            format(a, contenedor);
            break;
        case 'b':
            b = document.querySelector("#plazo_meses").value.replaceAll('´', '');
            var contenedor = '#plazo_meses';
            var QuitarComa = b.replace(',', '');
            b = QuitarComa.replaceAll(/\.{2,}/g, '.');
            format(b, contenedor);
            break;
        case 'c':
            c = document.querySelector("#tasa_interes").value.replaceAll('´', '');
            var contenedor = '#tasa_interes';
            var QuitarComa = c.replace(',', '');
            c = QuitarComa.replaceAll(/\.{2,}/g, '.');
            format(c, contenedor);
            break;
        case 'e':
            e = document.querySelector("#cantidad_actual").value.replaceAll('´', '');
            var contenedor = '#cantidad_actual';
            var QuitarComa = e.replace(',', '');
            e = QuitarComa.replaceAll(/\.{2,}/g, '.');
            format(e, contenedor);
            break;
        case 'r':
            r = document.querySelector("#ahorro_mensual").value.replaceAll('´', '');
            var contenedor = '#ahorro_mensual';
            var QuitarComa = r.replace(',', '');
            r = QuitarComa.replaceAll(/\.{2,}/g, '.');
            format(r, contenedor);
            break;
        case 'r2':
            r2 = document.querySelector("#textResultadosDosCuantoDebo").value.replaceAll('´', '');
            var contenedor = '#textResultadosDosCuantoDebo';
            var QuitarComa = r2.replace(',', '');
            r2 = QuitarComa.replaceAll(/\.{2,}/g, '.');
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

    jQuery(contenedor).val(resultado + sepDecimal + splitRight.replaceAll('´', ''));
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
        alert("El monto en meta de ahorro debe ser mayor a cero");
    } else {
        if (b == '') {
            alert("Debes completar el campo de plazo (meses)");
        } else {
            if (c == '') {
                alert("Debes completar el campo de tasa de interés.");
            } else {
                var potencia = 1 + ((c / 100) / 12);
                var cCalUno = Math.pow(potencia, b);
                var cCalDos = Math.pow(potencia, b) - (1);
                var resultado = ((c / 100) / 12) * ((a - (e * cCalUno)) / cCalDos);
                var resultadoDos = a - (resultado * b);
                document.querySelector("#ahorro_mensual").value = parseFloat(resultado).toFixed(2);
                formatNumerico('r');

            };
        };
    };
};




window.addEventListener("pageshow", () => {
    jQuery("#categoria").val("Meta de ahorro");
});