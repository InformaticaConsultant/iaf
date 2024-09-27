

function formatNumericoFe(valor) {
    var resultado = "";
    var separador = ","; // separador para los miles
    var sepDecimal = '.'; // separador para los decimales
    let contenedor;
    let QuitarComa;
    let a = 0;
    let b = 0;
    let c = 0;
    let d = 0;
    let e = 0;
    let r = 0;
    let r2 = 0;

    switch (valor) {
        case 'a':
            a = jQuery("#ingreso").val();
             contenedor = '#ingreso';
             QuitarComa = a.replace(',', '');
            a = QuitarComa;
            format(a, contenedor);
            break;
        case 'b':
            b = jQuery("#alimentacion").val();
             contenedor = '#alimentacion';
             QuitarComa = b.replace(',', '');
            b = QuitarComa;
            format(b, contenedor);
            break;
        case 'c':
            c = jQuery("#vivienda").val();
             contenedor = '#vivienda';
             QuitarComa = c.replace(',', '');
            c = QuitarComa;
            format(c, contenedor);
            break;
        case 'd':
            e = jQuery("#servicio_basico").val();
             contenedor = '#servicio_basico';
             QuitarComa = e.replace(',', '');
            e = QuitarComa;
            format(e, contenedor);
            break;
        case 'e':
            r = jQuery("#educacion").val();
             contenedor = '#educacion';
             QuitarComa = r.replace(',', '');
            r = QuitarComa;
            format(r, contenedor);
            break;
        case 'f':
            r = jQuery("#transporte").val();
             contenedor = '#transporte';
             QuitarComa = r.replace(',', '');
            r = QuitarComa;
            format(r, contenedor);
            break;
        case 'g':
            r = jQuery("#salud").val();
             contenedor = '#salud';
             QuitarComa = r.replace(',', '');
            r = QuitarComa;
            format(r, contenedor);
            break;
        case 'h':
            r = jQuery("#seguros").val();
             contenedor = '#seguros';
             QuitarComa = r.replace(',', '');
            r = QuitarComa;
            format(r, contenedor);
            break;
        case 'r1':
            r2 = jQuery("#gasto_mensual").val();
             contenedor = '#gasto_mensual';
             QuitarComa = r2.replace(',', '');
            r2 = QuitarComa;
            format(r2, contenedor);
            break;
        case 'r2':
            r2 = jQuery("#fondo_basico").val();
             contenedor = '#fondo_basico';
             QuitarComa = r2.replace(',', '');
            r2 = QuitarComa;
            format(r2, contenedor);
            break;
        case 'r3':
            r2 = jQuery("#fondo_robusto").val();
             contenedor = '#fondo_robusto';
             QuitarComa = r2.replace(',', '');
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

function calcularFondos() {
    var inputs = document.querySelectorAll(".form1 input:not([disabled])");
    const gasto_mensual_ref = document.querySelector("#gasto_mensual");
    const fondo_basico_ref = document.querySelector("#fondo_basico");
    const fondo_robusto_ref = document.querySelector("#fondo_robusto");
    var gasto_mensual = 0;
    var fondo_basico = 0;
    var fondo_robusto = 0;
    for (const key in inputs) {
        if (Object.hasOwnProperty.call(inputs, key) && key != 0) {
            const element = inputs[key];
            element.value ? gasto_mensual += parseFloat(element.value.replace(',', '')) : gasto_mensual;
        }
    }
    gasto_mensual_ref.value = gasto_mensual;
    fondo_basico_ref.value = gasto_mensual * 3;
    fondo_robusto_ref.value = gasto_mensual * 6;
    formatNumericoFe('r1');
    formatNumericoFe('r2');
    formatNumericoFe('r3');
}




window.addEventListener("pageshow", () => {
    jQuery("#categoria").val("Fondos de emergencia");
});