const getById = id => document.getElementById(id);
// $.noConflict();

function enviarDatos() {
    let edadActual = parseInt( jQuery("#edadActual").val() || "0");
    let edadRetiro = parseInt( jQuery("#edadRetiro").val() || "0");
    if(edadActual <18){
        alert("La edad actual debe de ser mayor a los 18 años.");
        getById('edadActual').focus();
        return;
    }

    if(edadRetiro < 55 || edadRetiro > 110 ){
        alert("La edad de retiro no debe de ser menor de 55, ni mayor de 110 años.");
        getById('edadRetiro').focus();
        return;
    }
    CalcularPensionReq ={
        genero: "M",

        montoAcumuladoCCI: jQuery("#montoAcumuladoCCI").val().replace(/,/g, '') || "0",
        salarioActual: jQuery("#salarioActual").val().replace(/,/g, '') || "0",
        porcentajeExtra: jQuery("#porcentajeExtra").val().replace(/,/g, '') || "0",
        aporteVoluntario: jQuery("#aporteVoluntario").val().replace(/,/g, '') || "0",
        edadActual: jQuery("#edadActual").val() || "0",
        edadRetiro: jQuery("#edadRetiro").val() || "0"
    }

    console.log(CalcularPensionReq);
    $.ajax({
        url: 'https://api.bpd.com.do/bpd/sb/afpcalculadora/calcularpension',
        type: 'POST',
        dataType: 'text',
        data: JSON.stringify({
            "HEADER": {
                "CabeceroReq": {
                    "canal": "Mobile",
                    "servidorRemoto": "",
                    "informacionCliente": {
                        "tipoDocumento": "CEDULA",
                        "numDocumento": "",
                        "usuario": ""
                    }
                }
            },
            BODY: {
                CalcularPensionReq: {
                    genero: "M",

                    montoAcumuladoCCI: jQuery("#montoAcumuladoCCI").val().replace(/,/g, '') || "0",
                    salarioActual: jQuery("#salarioActual").val().replace(/,/g, '') || "0",
                    porcentajeExtra: jQuery("#porcentajeExtra").val().replace(/,/g, '') || "0",
                    aporteVoluntario: jQuery("#aporteVoluntario").val().replace(/,/g, '') || "0",
                    edadActual: jQuery("#edadActual").val() || "0",
                    edadRetiro: jQuery("#edadRetiro").val() || "0",
                }
            }
        }),
        beforeSend: function(xhr) {
            xhr.setRequestHeader('x-ibm-client-id', '0acea54b-9bac-4b6f-858a-83499c57c562');
        }
    }).done(res => {
        //Scroll to results
        const id = 'results';
        const yOffset = -170;
        const element = document.getElementById(id);
        const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;

        window.scrollTo({ top: y, behavior: 'smooth' });

        //Fill in the data
        const data = JSON.parse(res);
        [
            'añoPension',
            'montoConstitutivo',
            'montoConstitutivoAV',
            'ultimoSalario',
            'pensionMensual',
            'pensionMensualAV',
            'tasaReemplazos',
            'tasaReemplazosAV',
        ].map(field => {
            format(data.Body.CalcularPensionRes[field], '#r' + field)
                // getById('r' + field).value = data.Body.CalcularPensionRes[field];
        })
    });
}

function formatNumerico(valor) {
    let a = 0;
    let b = 0;
    let c = 0;
    let d = 0;
    let r = 0;
    let r2 = 0;

    let contenedor;
    let QuitarComa;

    switch (valor) {
        case 'a':
            a = jQuery("#montoAcumuladoCCI").val();
             contenedor = '#montoAcumuladoCCI';
             QuitarComa = a.replace(',', '');
            a = QuitarComa;
            format(a, contenedor);
            break;
        case 'b':
            b = jQuery("#salarioActual").val();
             contenedor = '#salarioActual';
             QuitarComa = b.replace(',', '');
            b = QuitarComa;
            format(b, contenedor);
            break;
        case 'c':
            c = jQuery("#porcentajeExtra").val();
             contenedor = '#porcentajeExtra';
             QuitarComa = c.replace(',', '');
            c = QuitarComa;
            format(c, contenedor);
            break;
        case 'd':
            d = jQuery("#aporteVoluntario").val();
             contenedor = '#aporteVoluntario';
             QuitarComa = d.replace(',', '');
            d = QuitarComa;
            format(d, contenedor);
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


function numberValidatorPension(event, withPoint = true) {

    let allowedSpecialKeys = [8, 9, 13, 37, 38, 39, 40];
    let patron = withPoint ? /[0-9.]/ : /[0-9]/;
    let key = event.key;
    if (patron.test(key) || allowedSpecialKeys.includes(event.keyCode)) {
        return true;
    } else {
        return false;
    }
}




window.addEventListener("pageshow", () => {
    jQuery("#categoria").val("Plan de retiro");
});