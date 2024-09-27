console.log("Calculadoras de prestamos vehiculo");

// try {
//     var isIE = /*@cc_on!@*/ false || !!document.documentMode; //IE Support

//     if (isIE) {

//         let myScript = document.createElement("script");
//         myScript.setAttribute("src", "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js");
//         document.body.appendChild(myScript);
//     }

// } catch (error) {
//     console.log(error);
// }


// let myScript = document.createElement("script");
// myScript.setAttribute("src", "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js");
// document.body.appendChild(myScript);



/* Personal Loan Calculator
   http://66.98.67.3/SolicitudesBPD/Productos/Calc0km.aspx
  Taken from source file
 */

var tipo = getUrlVars()["tipo"];
var flujo, rangoAno, newLightN1, newLightN2, newLightN3, newLightN4, newVanN1, newVanN2, newVanN3, newVanN4, newJeepetaN1, newJeepetaN2, newJeepetaN3;
var newJeepetaN4, newHeavyN1, newHeavyN2, newHeavyN3, newHeavyN4, usedLightN1, usedLightN2, usedLightN3, usedLightN4, usedVanN1, usedVanN2, usedVanN3;
var usedVanN4, usedJeepetaN1, usedJeepetaN2, usedJeepetaN3, usedJeepetaN4, usedHeavyN1, usedHeavyN2, usedHeavyN3, usedHeavyN4, precioMaximo1;
var precioMaximo2, precioMaximo3, precioMaximo4;


//INICIO NEORIS: Funciones para llenado de combo VersionVehiculo, Año y Cantidad de cuota.
function loadpage() {
    getParameterRest();
    document.forms['CalcForm'].elements['FechaDesembolso'].value = getDateValue(new Date()); //ChangeStartDate();
    /*flujo = 1;
    rangoAno = 5;
    newLightN1 = 5.90;
    newLightN2 = 5.01;
    newLightN3 = 4.48;
    newLightN4 = 4.35;
    newVanN1 = 6.08;
    newVanN2 = 5.50;
    newVanN3 = 4.65;
    newVanN4 = 4.53;
    newJeepetaN1 = 5.63;
    newJeepetaN2 = 4.47;
    newJeepetaN3 = 3.89;
    newJeepetaN4 = 3.73;
    newHeavyN1 = 6.91;
    newHeavyN2 = 6.27;
    newHeavyN3 = 5.34;
    newHeavyN4 = 5.20;
    usedLightN1 = 6.81;
    usedLightN2 = 5.73;
    usedLightN3 = 5.19;
    usedLightN4 = 5.05;
    usedVanN1 = 6.99;
    usedVanN2 = 6.33;
    usedVanN3 = 5.35;
    usedVanN4 = 5.21;
    usedJeepetaN1 = 6.74;
    usedJeepetaN2 = 5.48;
    usedJeepetaN3 = 4.86;
    usedJeepetaN4 = 4.69;
    usedHeavyN1 = 7.95;
    usedHeavyN2 = 7.21;
    usedHeavyN3 = 6.14;
    usedHeavyN4 = 5.98;
    fillcomboVersionVehiculo();
    fillcomboYear();
    Mensaje0Km();*/
}

function getSafePercentage() {
    // var spUrl1 = location.protocol + "//" + location.hostname + "/_api/web/lists/getbytitle('SafePercentage')/items?$filter=Title eq 'values'";
    var spUrl1 = "https://www.popularenlinea.com/_api/web/lists/getbytitle('SafePercentage')/items?$filter=Title eq 'values'";

    $.ajax({
        url: spUrl1,
        method: "GET",
        headers: { "Accept": "application/json; odata=verbose" },
        success: function(data) {
            if (data.d.results.length > 0) {}
        },
        error: function(data) {
            //TODO:
        }
    }).done(function(data) {
        if (data.d.results.length > 0) {

            //Obteniendo el flujo.
            var aResult = data.d.results[0];

            if (aResult.NewLightN1 != null) {
                newLightN1 = aResult.NewLightN1;
            }

            if (aResult.NewLightN2 != null) {
                newLightN2 = aResult.NewLightN2;
            }

            if (aResult.NewLightN3 != null) {
                newLightN3 = aResult.NewLightN3;
            }

            if (aResult.NewLightN4 != null) {
                newLightN4 = aResult.NewLightN4;
            }

            if (aResult.NewVanN1 != null) {
                newVanN1 = aResult.NewVanN1;
            }

            if (aResult.NewVanN2 != null) {
                newVanN2 = aResult.NewVanN2;
            }

            if (aResult.NewVanN3 != null) {
                newVanN3 = aResult.NewVanN3;
            }

            if (aResult.NewVanN4 != null) {
                newVanN4 = aResult.NewVanN4;
            }

            if (aResult.NewJeepetaN1 != null) {
                newJeepetaN1 = aResult.NewJeepetaN1;
            }

            if (aResult.NewJeepetaN2 != null) {
                newJeepetaN2 = aResult.NewJeepetaN2;
            }

            if (aResult.NewJeepetaN3 != null) {
                newJeepetaN3 = aResult.NewJeepetaN3;
            }

            if (aResult.NewJeepetaN4 != null) {
                newJeepetaN4 = aResult.NewJeepetaN4;
            }

            if (aResult.NewHeavyN1 != null) {
                newHeavyN1 = aResult.NewHeavyN1;
            }

            if (aResult.NewHeavyN2 != null) {
                newHeavyN2 = aResult.NewHeavyN2;
            }

            if (aResult.NewHeavyN3 != null) {
                newHeavyN3 = aResult.NewHeavyN3;
            }

            if (aResult.NewHeavyN4 != null) {
                newHeavyN4 = aResult.NewHeavyN4;
            }

            if (aResult.UsedLightN1 != null) {
                usedLightN1 = aResult.UsedLightN1;
            }

            if (aResult.UsedLightN2 != null) {
                usedLightN2 = aResult.UsedLightN2;
            }

            if (aResult.UsedLightN3 != null) {
                usedLightN3 = aResult.UsedLightN3;
            }

            if (aResult.UsedLightN4 != null) {
                usedLightN4 = aResult.UsedLightN4;
            }

            if (aResult.UsedVanN1 != null) {
                usedVanN1 = aResult.UsedVanN1;
            }

            if (aResult.UsedVanN2 != null) {
                usedVanN2 = aResult.UsedVanN2;
            }

            if (aResult.UsedVanN3 != null) {
                usedVanN3 = aResult.UsedVanN3;
            }

            if (aResult.UsedVanN4 != null) {
                usedVanN4 = aResult.UsedVanN4;
            }

            if (aResult.UsedJeepetaN1 != null) {
                usedJeepetaN1 = aResult.UsedJeepetaN1;
            }

            if (aResult.UsedJeepetaN2 != null) {
                usedJeepetaN2 = aResult.UsedJeepetaN2;
            }

            if (aResult.UsedJeepetaN3 != null) {
                usedJeepetaN3 = aResult.UsedJeepetaN3;
            }

            if (aResult.UsedJeepetaN4 != null) {
                usedJeepetaN4 = aResult.UsedJeepetaN4;
            }

            if (aResult.UsedHeavyN1 != null) {
                usedHeavyN1 = aResult.UsedHeavyN1;
            }

            if (aResult.UsedHeavyN2 != null) {
                usedHeavyN2 = aResult.UsedHeavyN2;
            }

            if (aResult.UsedHeavyN3 != null) {
                usedHeavyN3 = aResult.UsedHeavyN3;
            }

            if (aResult.UsedHeavyN4 != null) {
                usedHeavyN4 = aResult.UsedHeavyN4;
            }

            if (aResult.PrecioMaximo1 != null) {
                precioMaximo1 = aResult.PrecioMaximo1;
            }

            if (aResult.PrecioMaximo2 != null) {
                precioMaximo2 = aResult.PrecioMaximo2;
            }

            if (aResult.PrecioMaximo3 != null) {
                precioMaximo3 = aResult.PrecioMaximo3;
            }

            if (aResult.PrecioMaximo4 != null) {
                precioMaximo4 = aResult.PrecioMaximo4;
            }
        }
    })
}

function getParameterRest() {
    // var spUrl = location.protocol + "//" + location.hostname + "/_api/web/lists/getbytitle('ListParametrica')/items?$filter=Title eq 'values'";
    var spUrl = "https://www.popularenlinea.com/_api/web/lists/getbytitle('ListParametrica')/items?$filter=Title eq 'values'";

    $.ajax({
        url: spUrl,
        method: "GET",
        headers: { "Accept": "application/json; odata=verbose" },
        success: function(data) {
            if (data.d.results.length > 0) {
                //printRates(data.d.results[0]);
            }
        },
        error: function(data) {
            //TODO:
        }
    }).done(function(data) {
            if (data.d.results.length > 0) {

                //Obteniendo el flujo.    
                var aResult = data.d.results[0];

                if (aResult.flujo != null) {
                    flujo = aResult.flujo;
                }

                if (aResult.yearRange != null) {
                    rangoAno = aResult.yearRange;
                }

                //

                if (flujo == "" || flujo == undefined) {
                    flujo = getUrlVars()["flujo"];
                }

                if (rangoAno == "" || rangoAno == undefined) {
                    rangoAno = 5;
                }

                getSafePercentage();
                fillcomboVersionVehiculo();
                fillcomboYear();
                Mensaje0Km();
            }
        }

    );
}

function getUrlVars() {

    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi,
        function(m, key, value) {
            vars[key] = value;
        });
    return vars;
}

function Mensaje0Km() {
    if (tipo == 1 || tipo == 3) {
        document.getElementById("Mensaje0Km").style.display = 'block';
    } else {
        document.getElementById("Mensaje0Km").style.display = 'none';
    }
}

function fillcomboVersionVehiculo() {

    if (tipo == 1 || tipo == 3) {
        var version = ["Americanos", "Europeos", "Vehículos de lujo", "Chinos", "Japoneses", "Coreanos"];
    } else {
        var version = ["Americanos", "Europeos", "Vehículos de lujo", "Japoneses", "Coreanos"];
    }
    var select = document.getElementById("VersionVehiculo");
    for (var i = 0; i < version.length; i++) {

        if (i == 0) {
            select.options[i] = new Option(version[i], version[i], true, true);
        } else {
            select.options[i] = new Option(version[i]);
        }
    }
    ChangeVersion();
    /*
    if (flujo == 1) {
        document.forms["CalcForm"].elements["VersionVehiculo"].value = select.options[0];
    }
    */
}

function fillcomboYear() {

    var dt = new Date();
    var year = dt.getFullYear();
    var anos;
    if (tipo == 1 || tipo == 3) {
        anos = [year, year - 1];
    } else {
        for (var i = rangoAno; i >= 0; i--) {
            if (anos == undefined) {
                anos = [(year)];
            } else {
                anos.push(year);
            }
            year = year - 1;
        }
    }

    var select = document.getElementById("Ano");
    for (var i = 0; i < anos.length; i++) {
        select.options[i] = new Option(anos[i]);
    }



    if (((document.forms["CalcForm"].elements["NoCuotas"].value) == "" && (flujo == 2)) || ((document.forms["CalcForm"].elements["NoCuotas"].value) == undefined && (flujo == 2))) {
        var cantcuotas = ["6", "12", "18", "24", "30", "36", "42", "48", "54", "60", "66", "72", "78", "84"];
        var select = document.getElementById("NoCuotas");
        for (var i = 0; i < cantcuotas.length; i++) {
            select.options[i] = new Option(cantcuotas[i]);
        }
        document.forms["CalcForm"].elements["NoCuotas"].selectedIndex = (i - 1);
    } else if (((document.forms["CalcForm"].elements["NoCuotas"].value) == "" && (flujo == 1) && (tipo == 2)) || ((document.forms["CalcForm"].elements["NoCuotas"].value) == undefined && (flujo == 1) && (tipo == 2))) {
        var cantcuotas = ["6", "12", "18", "24", "30", "36", "42", "48"];
        var select = document.getElementById("NoCuotas");
        for (var i = 0; i < cantcuotas.length; i++) {
            select.options[i] = new Option(cantcuotas[i]);
        }
        document.forms["CalcForm"].elements["NoCuotas"].selectedIndex = (i - 1);
    }
}

function getSelectedComboVersionVehiculo() {
    var select = document.getElementById("VersionVehiculo");
    var index = select.selectedIndex;
    var value = select.options[index].value;
    var text = select.options[index].text;
    return value;
}

function getSelectedAno() {
    var select = document.getElementById("Ano");
    var index = select.selectedIndex;
    var value = select.options[index].value;
    var text = select.options[index].text;
    return value;
}

function getSelectedNoCuota() {
    var select = document.getElementById("NoCuotas");
    var index = select.selectedIndex;
    var value = select.options[index].value;
    var text = select.options[index].text;
    return value;
}

function ChangeVersion() {
    var dt = new Date();
    if (tipo == 1 || tipo == 3) {
        if (getSelectedComboVersionVehiculo() != "Chinos") {
            var cantcuotas = ["6", "12", "18", "24", "30", "36", "42", "48", "54", "60", "66", "72", "78", "84"];
        } else {
            var cantcuotas = ["6", "12", "18", "24", "30", "36", "42", "48", "54", "60"];
        }
        var select = document.getElementById("NoCuotas");
        for (var i = 0; i < cantcuotas.length; i++) {
            select.options[i] = new Option(cantcuotas[i]);
        }
        document.forms["CalcForm"].elements["NoCuotas"].selectedIndex = (i - 1);
    } else {
        if (flujo == 1) {
            var cantcuotas = ["6", "12", "18", "24", "30", "36", "42", "48"];
            var select = document.getElementById("NoCuotas");
            for (var i = 0; i < cantcuotas.length; i++) {
                select.options[i] = new Option(cantcuotas[i]);
            }
            document.forms["CalcForm"].elements["NoCuotas"].selectedIndex = (i - 1);
        }
    }
    if (flujo != 2) {
        document.forms["CalcForm"].elements["ValorVehiculo"].value = "";
        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
        document.forms["CalcForm"].elements["InicialPagar"].value = "";
        document.forms["CalcForm"].elements["PagoInmediato"].value = "";
        document.forms["CalcForm"].elements["Ano"].selectedIndex = 0;

        // document.forms["CalcForm"].elements["Ano"].options[0].value = 0;
        // document.forms["CalcForm"].elements["Ano"].options[0].text = dt.getFullYear();
        document.forms["CalcForm"].elements["SAno1"].value = "";
        document.forms["CalcForm"].elements["CuotaFinanciamiento"].value = "";
        document.forms["CalcForm"].elements["CuotaFinanciamientoTradicional"].value = "";
        document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value = "";
        document.forms["CalcForm"].elements["LimiteAnualFinanciamiento"].value = "";
        document.forms["CalcForm"].elements["Diferencia"].value = "";
    }

    if (document.forms["CalcForm"].elements["FechaCancelacion"].value == "") {
        document.forms["CalcForm"].elements["FechaCancelacion"].value = ChangeStartDate();
    }
}

function ChangeYear() {
    if (flujo == 2) {
        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
        document.forms["CalcForm"].elements["InicialPagar"].value = "";
        document.forms["CalcForm"].elements["PagoInmediato"].value = "";

        var dt = new Date();
        var year = dt.getFullYear();
        if (getSelectedAno() == year) {
            var cantcuotas = ["6", "12", "18", "24", "30", "36", "42", "48", "54", "60", "66", "72", "78", "84"];
        } else if ((getSelectedAno() == (year - 1)) || (getSelectedAno() == (year - 2))) {
            var cantcuotas = ["6", "12", "18", "24", "30", "36", "42", "48", "54", "60", "66", "72"];
        } else {
            var cantcuotas = ["6", "12", "18", "24", "30", "36", "42", "48", "54", "60"];
        }
        var select = document.getElementById("NoCuotas");
        for (var i = 0; i < cantcuotas.length; i++) {
            select.options[i] = new Option(cantcuotas[i]);
        }

        document.forms["CalcForm"].elements["NoCuotas"].selectedIndex = (i - 1);

        if (document.forms["CalcForm"].elements["FechaCancelacion"].value == "") {
            // debugger;
            document.forms["CalcForm"].elements["FechaCancelacion"].value = ChangeStartDate();
        }

        ChangeMontoVehiculo();
    }
}
//FIN NEORIS: Funciones para llenado de combos VersionVehiculo, Año y Cantidad de cuotas.


function getObj(objid) {
    if (document.getElementById)
        return document.getElementById(objid);
    else if (document.all)
        return document.all(objid);
    return null;
}

var months = new Array("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre");

//INICIO NEORIS: Se modifica función para el cálculo de pagos extraordinarios.
function PC(op) {
    if (tipo == 3) {
        return Math.round(op * 0.50) / 4;
    } else {
        return Math.round(op * 0.40) / 4;
    }
}
//FIN NEORIS: Se modifica función para el cálculo de pagos extraordinarios.

function FormatDate(fecha) {
    return months[fecha.getMonth()] + " - " + fecha.getFullYear();
}

function TransformNumber(valor) {
    valor = "" + valor;
    return valor.replace(/,/g, "");
}

function CheckExtraPay(source, value) {
    var valor = parseFloat(TransformNumber("0" + document.forms["CalcForm"].elements["ExtraPay"].value));

    //var pos = 0;
    //for(;pos<4;pos++)
    //	if(document.forms["CalcForm"].elements["Extra" + (pos + 2)].checked == true)
    //		 valor += parseFloat(TransformNumber(document.forms["CalcForm"].elements["ExtraPay"].value));


    //value.IsValid = (valor <= parseFloat(TransformNumber(document.forms["CalcForm"].elements["MontoFinanciamiento"].value)) * 0.40);
    value.IsValid = (valor <= parseFloat(TransformNumber("0" + document.forms["CalcForm"].elements["LimiteAnualFinanciamiento"].value)));
    /*document.all.NoCuotas.disabled = !value.IsValid;
    document.all.TasaInteres.disabled = !value.IsValid;
    document.forms["CalcForm"].elements["Categoria"].disabled = !value.IsValid;
    document.all.ValorVehiculo.disabled = !value.IsValid;
    document.all.MontoFinaciar.disabled = !value.IsValid;
    document.all.FechaDesembolso.disabled = !value.IsValid;
    document.forms["CalcForm"].elements["DateSelector"].disabled = !value.IsValid;*/
}

function TransformCurrency(valor) {
    //valor.value.length
    valor = TransformNumber(valor);

    var re = new RegExp("([0-9]*)([^0-9]?)([0-9]*)");
    var arr = re.exec(valor);
    var pos = RegExp.$1.length;
    valor = "";
    var count = 0;

    for (; pos;) {
        if (count++ % 3 == 0 && count > 1)
            valor = "," + valor;

        valor = RegExp.$1.charAt(--pos) + valor;
    }

    if (valor == "")
        valor = "0";

    return valor = valor + "." + (RegExp.$3 + "00").match("[0-9]{2}");
}

function CalcGastosInscripcion(valor) {
    return 0;
    gi = 0;
    if (valor > 0 && valor < 700000)
        gi = 8100;
    else if (valor >= 700000 && valor < 1500000)
        gi = 12100;
    else if (valor >= 1500000)
        gi = 24100;
    return TransformCurrency(gi);
}

//INICIO NEORIS: Se modifica function para cambio en calculadora de préstamos de vehículos, esto para valor de vehículo.
function ChangeMontoVehiculo() {
    var valorVehiculo = TransformNumber(document.forms["CalcForm"].elements["ValorVehiculo"].value);
    if (valorVehiculo <= 0) {
        alert("Capturar el valor del vehículo.");
        //document.forms["CalcForm"].elements["ValorVehiculo"].focus();
        //document.location.reload();
        return;
    }

    var value = getSelectedComboVersionVehiculo();
    if ((typeof(Page_ClientValidate) != 'function' || Page_ClientValidate())) {
        if (tipo == 1 || tipo == 3) {
            if (value == "Chinos") {
                if (valorVehiculo < ((10000 * 100) / 60)) {
                    alert("El valor del vehículo debe de ser mínimo de RD$ " + TransformCurrency((10000 * 100) / 60) + ".");
                    document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                } else if (valorVehiculo > ((9999999 * 100) / 60)) {
                    document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                    var valorFinanciamiento = 9999999;
                } else {
                    var valorFinanciamiento = valorVehiculo * 0.60;
                    if (document.forms["CalcForm"].elements["MontoFinanciar"].value > valorFinanciamiento) {
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else if ((document.forms["CalcForm"].elements["MontoFinanciar"].value = "") || (document.forms["CalcForm"].elements["MontoFinanciar"].value = "0.00")) {
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    }
                }
            } else {
                if (valorVehiculo < ((100000.01 * 100) / 80)) {
                    alert("El valor del vehículo debe de ser mínimo de RD$ " + TransformCurrency((100000.01 * 100) / 80) + ".");
                    document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                } else if (valorVehiculo > ((1000000 * 100) / 80)) {
                    document.forms["CalcForm"].elements["MontoFinanciar"].value = 1000000;
                    var valorFinanciamiento = 1000000;
                } else {
                    var valorFinanciamiento = valorVehiculo * 0.80;
                    if (document.forms["CalcForm"].elements["MontoFinanciar"].value > valorFinanciamiento) {
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else if ((document.forms["CalcForm"].elements["MontoFinanciar"].value = "") || (document.forms["CalcForm"].elements["MontoFinanciar"].value = "0.00")) {
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    }
                }
            }
        } else {
            if (flujo == 1) {
                if ((value == "Japoneses") || (value == "Coreanos")) {
                    if (valorVehiculo < ((10000 * 100) / 90)) {
                        alert("El valor del vehículo debe de ser mínimo de RD$ " + TransformCurrency((10000 * 100) / 90) + ".");
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                    } else if (valorVehiculo > ((9999999 * 100) / 90)) {
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                        var valorFinanciamiento = 9999999;
                    } else {
                        var valorFinanciamiento = valorVehiculo * 0.90;
                        if (document.forms["CalcForm"].elements["MontoFinanciar"].value > valorFinanciamiento) {
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                        } else if ((document.forms["CalcForm"].elements["MontoFinanciar"].value = "") || (document.forms["CalcForm"].elements["MontoFinanciar"].value = "0.00")) {
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                        }
                    }
                } else {
                    if (valorVehiculo < ((10000 * 100) / 80)) {
                        alert("El valor del vehículo debe de ser mínimo de RD$ " + TransformCurrency((10000 * 100) / 80) + ".");
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                    } else if (valorVehiculo > ((9999999 * 100) / 80)) {
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                        var valorFinanciamiento = 9999999;
                    } else {
                        var valorFinanciamiento = valorVehiculo * 0.80;
                        if (document.forms["CalcForm"].elements["MontoFinanciar"].value > valorFinanciamiento) {
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                        } else if ((document.forms["CalcForm"].elements["MontoFinanciar"].value = "") || (document.forms["CalcForm"].elements["MontoFinanciar"].value = "0.00")) {
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                        }
                    }
                }
            } else {
                var ano = getSelectedAno();
                var dt = new Date();
                var year = dt.getFullYear();
                if (ano == year) {
                    if (valorVehiculo < ((10000 * 100) / 90)) {
                        alert("El valor del vehículo debe de ser mínimo de RD$ " + TransformCurrency((10000 * 100) / 90) + ".")
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                    } else if (valorVehiculo > ((9999999 * 100) / 90)) {
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                        var valorFinanciamiento = 9999999;
                    } else {
                        var valorFinanciamiento = valorVehiculo * 0.90;
                        if (document.forms["CalcForm"].elements["MontoFinanciar"].value > valorFinanciamiento) {
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                        } else if ((document.forms["CalcForm"].elements["MontoFinanciar"].value = "") || (document.forms["CalcForm"].elements["MontoFinanciar"].value = "0.00")) {
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                        }
                    }
                } else if (ano == (year - 1)) {
                    if (valorVehiculo < ((10000 * 100) / 85)) {
                        alert("El valor del vehículo debe de ser mínimo de RD$ " + TransformCurrency((10000 * 100) / 85) + ".")
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                    } else if (valorVehiculo > ((9999999 * 100) / 85)) {
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                        var valorFinanciamiento = 9999999;
                    } else {
                        var valorFinanciamiento = valorVehiculo * 0.85;
                        if (document.forms["CalcForm"].elements["MontoFinanciar"].value > valorFinanciamiento) {
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                        } else if ((document.forms["CalcForm"].elements["MontoFinanciar"].value = "") || (document.forms["CalcForm"].elements["MontoFinanciar"].value = "0.00")) {
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                        }
                    }
                } else {
                    if (valorVehiculo < ((10000 * 100) / 80)) {
                        alert("El valor del vehículo debe de ser mínimo de RD$ " + TransformCurrency((10000 * 100) / 80) + ".")
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                    } else if (valorVehiculo > ((9999999 * 100) / 80)) {
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                        var valorFinanciamiento = 9999999;
                    } else {
                        var valorFinanciamiento = valorVehiculo * 0.80;
                        if (document.forms["CalcForm"].elements["MontoFinanciar"].value > valorFinanciamiento) {
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                        } else if ((document.forms["CalcForm"].elements["MontoFinanciar"].value = "") || (document.forms["CalcForm"].elements["MontoFinanciar"].value = "0.00")) {
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                        }
                    }
                }
            }
        }
    }

    document.forms["CalcForm"].elements["InicialPagar"].value = TransformCurrency(valorVehiculo - valorFinanciamiento);
    document.forms["CalcForm"].elements["PCInicialPagar"].value = PC(TransformNumber(document.forms["CalcForm"].elements["InicialPagar"].value), valorVehiculo) + " %";
    document.forms["CalcForm"].elements["GastosInscripcion"].value = CalcGastosInscripcion(valorVehiculo);
    document.forms["CalcForm"].elements["LimiteAnualFinanciamiento"].value = TransformCurrency(PC(valorFinanciamiento));
    document.forms["CalcForm"].elements["PagoInmediato"].value = TransformCurrency(parseFloat(TransformNumber(document.forms["CalcForm"].elements["InicialPagar"].value)) + parseFloat(TransformNumber(document.forms["CalcForm"].elements["GastosInscripcion"].value)));
    document.forms["CalcForm"].elements["MontoFinanciar"].value = TransformCurrency(document.forms["CalcForm"].elements["MontoFinanciar"].value);
    document.forms["CalcForm"].elements["ValorVehiculo"].value = TransformCurrency(document.forms["CalcForm"].elements["ValorVehiculo"].value);
    ChangeCategory();
}
//FIN NEORIS: Se modifica function para cambio en calculadora de préstamos de vehículos, esto para valor de vehículo.

//INICIO NEORIS: Se agrega función para validación de que monto a financiar no sea mayor al precio del vehículo.
function ChangeMontoFinanciar() {
    var value = getSelectedComboVersionVehiculo();
    var valorVehiculo = TransformNumber(document.forms["CalcForm"].elements["ValorVehiculo"].value);
    if ((typeof(Page_ClientValidate) != 'function' || Page_ClientValidate())) {
        if (tipo == 1 || tipo == 3) {
            if (value == "Chinos") {
                var valorFinanciamiento = valorVehiculo * 0.60;
                var financiamiento = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value);
                if (financiamiento > 9999999) {
                    if (financiamiento > valorVehiculo) {
                        alert("El monto a financiar NO debe ser mayor al precio del vehículo.");
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                        valorFinanciamiento = 0;
                    } else {
                        alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(9999999));
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                        valorFinanciamiento = 9999999;
                    }
                } else if (financiamiento > valorFinanciamiento) {
                    alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(valorFinanciamiento) + ", ya que solo se financia, máximo, el 60% del valor del vehículo.");
                    document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                } else if (financiamiento < 10000) {
                    alert("El monto a financiar debe ser mayor a " + TransformCurrency(10000) + ".")
                    document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                } else {
                    valorFinanciamiento = financiamiento;
                }
            } else {
                var valorFinanciamiento = valorVehiculo * 0.80;
                var financiamiento = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value);
                if (financiamiento > 1000000) {
                    if (financiamiento > valorVehiculo) {
                        alert("El monto a financiar NO debe ser mayor al precio del vehículo.");
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                        valorFinanciamiento = 0;
                    } else {
                        alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(1000000));
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = 1000000;
                        valorFinanciamiento = 1000000;
                    }
                } else if (financiamiento > valorFinanciamiento) {
                    alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(valorFinanciamiento) + ", ya que solo se financia, máximo, el 80% del valor del vehículo.");
                    document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                } else if (financiamiento < 100000.01) {
                    alert("El monto a financiar debe ser mayor a RD$ " + TransformCurrency(100000.01) + ".")
                    document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                } else {
                    valorFinanciamiento = financiamiento;
                }
            }
        } else {
            if (flujo == 1) {
                if ((value == "Japoneses") || (value == "Coreanos")) {
                    var valorFinanciamiento = valorVehiculo * 0.90;
                    var financiamiento = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value);
                    if (financiamiento > 9999999) {
                        if (financiamiento > valorVehiculo) {
                            alert("El monto a financiar NO debe ser mayor al precio del vehículo.");
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                            valorFinanciamiento = 0;
                        } else {
                            alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(9999999));
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                            valorFinanciamiento = 9999999;
                        }
                    } else if (financiamiento > valorFinanciamiento) {
                        alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(valorFinanciamiento) + ", ya que solo se financia, máximo, el 90% del valor del vehículo.");
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else if (financiamiento < 10000) {
                        alert("El monto a financiar debe ser mayor a RD$ " + TransformCurrency(10000) + ".")
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else {
                        valorFinanciamiento = financiamiento;
                    }
                } else {
                    var valorFinanciamiento = valorVehiculo * 0.80;
                    var financiamiento = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value);
                    if (financiamiento > 9999999) {
                        if (financiamiento > valorVehiculo) {
                            alert("El monto a financiar NO debe ser mayor al precio del vehículo.");
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                            valorFinanciamiento = 0;
                        } else {
                            alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(9999999));
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                            valorFinanciamiento = 9999999;
                        }
                    } else if (financiamiento > valorFinanciamiento) {
                        alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(valorFinanciamiento) + ", ya que solo se financia, máximo, el 60% del valor del vehículo.");
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else if (financiamiento < 10000) {
                        alert("El monto a financiar debe ser mayor a RD$ " + TransformCurrency(10000) + ".")
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else {
                        valorFinanciamiento = financiamiento;
                    }
                }
            } else {
                var ano = getSelectedAno();
                var dt = new Date();
                var year = dt.getFullYear();
                if (ano == year) {
                    var valorFinanciamiento = valorVehiculo * 0.90;
                    var financiamiento = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value);
                    if (financiamiento > 9999999) {
                        if (financiamiento > valorVehiculo) {
                            alert("El monto a financiar NO debe ser mayor al precio del vehículo.");
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                            valorFinanciamiento = 0;
                        } else {
                            alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(9999999));
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                            valorFinanciamiento = 9999999;
                        }
                    } else if (financiamiento > valorFinanciamiento) {
                        alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(valorFinanciamiento) + ", ya que solo se financia, máximo, el 90% del valor del vehículo.");
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else if (financiamiento < 10000) {
                        alert("El monto a financiar debe ser mayor a " + TransformCurrency(10000) + ".")
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else {
                        valorFinanciamiento = financiamiento;
                    }
                } else if (ano == (year - 1)) {
                    var valorFinanciamiento = valorVehiculo * 0.85;
                    var financiamiento = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value);
                    if (financiamiento > 9999999) {
                        if (financiamiento > valorVehiculo) {
                            alert("El monto a financiar NO debe ser mayor al precio del vehículo.");
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                            valorFinanciamiento = 0;
                        } else {
                            alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(9999999));
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                            valorFinanciamiento = 9999999;
                        }
                    } else if (financiamiento > valorFinanciamiento) {
                        alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(valorFinanciamiento) + ", ya que solo se financia, máximo, el 85% del valor del vehículo.");
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else if (financiamiento < 10000) {
                        alert("El monto a financiar debe ser mayor a " + TransformCurrency(10000) + ".")
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else {
                        valorFinanciamiento = financiamiento;
                    }
                } else {
                    var valorFinanciamiento = valorVehiculo * 0.80;
                    var financiamiento = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value);
                    if (financiamiento > 9999999) {
                        if (financiamiento > valorVehiculo) {
                            alert("El monto a financiar NO debe ser mayor al precio del vehículo.");
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
                            valorFinanciamiento = 0;
                        } else {
                            alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(9999999));
                            document.forms["CalcForm"].elements["MontoFinanciar"].value = 9999999;
                            valorFinanciamiento = 9999999;
                        }
                    } else if (financiamiento > valorFinanciamiento) {
                        alert("El monto a financiar debe ser menor o igual a RD$ " + TransformCurrency(valorFinanciamiento) + ", ya que solo se financia, máximo, el 80% del valor del vehículo.");
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else if (financiamiento < 10000) {
                        alert("El monto a financiar debe ser mayor a " + TransformCurrency(10000) + ".")
                        document.forms["CalcForm"].elements["MontoFinanciar"].value = valorFinanciamiento;
                    } else {
                        valorFinanciamiento = financiamiento;
                    }
                }
            }
        }
    }
    //FIN NEORIS: Se agrega función para validación de que monto a financiar no sea mayor al precio del vehículo.

    //COMENTADO POR NEORIS: Código antes de cambio de monto a financiar.
    //				var valorFinanciar = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value);
    //				var valorFinanciamiento = valorFinanciar > valorVehiculo * 0.90 ? valorVehiculo * 0.90 : valorFinanciar;

    document.forms["CalcForm"].elements["InicialPagar"].value = TransformCurrency(valorVehiculo - valorFinanciamiento);
    //				document.forms["CalcForm"].elements["MontoFinanciamiento"].value = TransformCurrency(valorFinanciamiento);
    document.forms["CalcForm"].elements["PCInicialPagar"].value = PC(TransformNumber(document.forms["CalcForm"].elements["InicialPagar"].value), valorVehiculo) + " %";
    //				document.forms["CalcForm"].elements["PCMontoFinanciar"].value = PC(valorFinanciar,valorVehiculo) + " %";
    //				document.forms["CalcForm"].elements["PCMontoFinanciamiento"].value = PC(valorFinanciamiento,valorVehiculo) + " %";
    document.forms["CalcForm"].elements["GastosInscripcion"].value = CalcGastosInscripcion(valorVehiculo);
    document.forms["CalcForm"].elements["LimiteAnualFinanciamiento"].value = TransformCurrency(PC(valorFinanciamiento, 1000));
    document.forms["CalcForm"].elements["PagoInmediato"].value = TransformCurrency(parseFloat(TransformNumber(document.forms["CalcForm"].elements["InicialPagar"].value)) + parseFloat(TransformNumber(document.forms["CalcForm"].elements["GastosInscripcion"].value)));
    document.forms["CalcForm"].elements["MontoFinanciar"].value = TransformCurrency(document.forms["CalcForm"].elements["MontoFinanciar"].value);
    document.forms["CalcForm"].elements["ValorVehiculo"].value = TransformCurrency(document.forms["CalcForm"].elements["ValorVehiculo"].value);
    ChangeCategory();

    if (document.forms["CalcForm"].elements["MontoFinanciar"].value == "0.00")
        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";

    if (document.forms["CalcForm"].elements["MontoFinanciar"].value == "0.00")
        document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
}



function ChangeExtraPay() {
    if ((typeof(Page_ClientValidate) != 'function' || Page_ClientValidate()) && document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value != "") {
        var startFecha = new Date(Date.parse(document.forms["CalcForm"].elements["FechaDesembolso"].value));
        var endFecha = new Date(Date.parse(document.forms["CalcForm"].elements["DateSelector"].options[document.forms["CalcForm"].elements["DateSelector"].selectedIndex].value));
        var Interes = document.forms["CalcForm"].elements["txttasainteres"].value; //document.forms["CalcForm"].elements["TasaInteres"].value;

        var m = (endFecha.getFullYear() - startFecha.getFullYear()) * 12 + (endFecha.getMonth() - startFecha.getMonth());
        var x = Math.pow(((parseFloat(Interes) + 1200) / 1200.00), m);
        var Monto = parseFloat(TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value));
        var PCCategory = parseFloat(TransformNumber(document.forms["CalcForm"].elements["SAno1"].value));

        if (document.forms["CalcForm"].elements["MontoFinanciar"].value == "" || document.forms["CalcForm"].elements["ExtraPay"].value == "" || parseFloat(document.forms["CalcForm"].elements["ExtraPay"].value) == 0)
            document.forms["CalcForm"].elements["ExtraPay"].value = "";
        if (document.forms["CalcForm"].elements["ExtraPay"].value == "")
            document.forms["CalcForm"].elements["ExtraCuota"].value = "";
        else {
            //document.forms["CalcForm"].elements["ExtraCuota"].value = parseFloat(document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value) + parseFloat(document.forms["CalcForm"].elements["ExtraPay"].value);	
            //Monto -= parseFloat(document.forms["CalcForm"].elements["ExtraPay"].value);
            Monto -= Math.round((TransformNumber(document.forms["CalcForm"].elements["ExtraPay"].value) / x) * 100) / 100;
        }

        var pos = 0;
        //for(;pos<4;pos++){
        for (; pos < 3; pos++) {

            if (document.forms["CalcForm"].elements["Extra" + (pos + 2)].checked == true && getObj("Table6").rows[pos + 2].style.visibility != "hidden" && document.forms["CalcForm"].elements["MontoFinanciar"].value != "") {
                document.forms["CalcForm"].elements["ExtraPay" + (pos + 2)].value = TransformCurrency(document.forms["CalcForm"].elements["ExtraPay"].value);
                //document.all["ExtraCuota" + (pos + 2)].value = document.forms["CalcForm"].elements["ExtraCuota"].value;
                //endFecha = new Date(Date.parse(document.all["DateSelector" + (pos +2)].Value));
                endFecha = new Date(Date.parse(document.forms["CalcForm"].elements["DateSelector"].options[document.forms["CalcForm"].elements["DateSelector"].selectedIndex].value));
                endFecha.setFullYear(endFecha.getFullYear() + pos + 1);

                m = (endFecha.getFullYear() - startFecha.getFullYear()) * 12 + (endFecha.getMonth() - startFecha.getMonth());
                x = Math.pow(((parseFloat(Interes) + 1200) / 1200.00), m);
                Monto -= Math.round((TransformNumber(document.forms["CalcForm"].elements["ExtraPay"].value) / x) * 100) / 100;

            } else {
                document.forms["CalcForm"].elements["Extra" + (pos + 2)].checked = false;
                document.forms["CalcForm"].elements["ExtraPay" + (pos + 2)].value = "";
                document.forms["CalcForm"].elements["ExtraCuota" + (pos + 2)].value = "";
            }
        }


        //NEORIS: Se agrega función para plazos getSelectedNoCuota().
        var Month = getSelectedNoCuota();
        var temp = Math.pow(((parseFloat(Interes) + 1200) / 1200.00), Month);

        if (document.forms["CalcForm"].elements["MontoFinanciar"].value != "") {
            document.forms["CalcForm"].elements["CuotaFinanciamiento"].value = TransformCurrency(Math.round(((Monto * Interes * temp) / ((temp - 1) * 1200)) * 100) / 100);
            document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value = TransformCurrency(Math.round((PCCategory + parseFloat(TransformNumber(document.forms["CalcForm"].elements["CuotaFinanciamiento"].value))) * 100) / 100);
            document.forms["CalcForm"].elements["Diferencia"].value = TransformCurrency(Math.round((TransformNumber(document.forms["CalcForm"].elements["CuotaFinanciamientoTradicional"].value) - TransformNumber(document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value)) * 100) / 100);
        } else {
            document.forms["CalcForm"].elements["CuotaFinanciamiento"].value = "";
            document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value = "";
            document.forms["CalcForm"].elements["Diferencia"].value = "";
        }

        //document.forms["CalcForm"].elements["ExtraCuota"].value = parseFloat(document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value) + parseFloat(document.forms["CalcForm"].elements["ExtraPay"].value);	


        var cf = TransformNumber(document.forms[0].elements["CuotaFinanciamiento"].value);
        var seg;

        var m = Month / 12;
        for (var x = 1; x < 2; x++) {
            seg = TransformNumber(document.forms[0].elements["SAno" + x].value)
            if (x < m + 1) {
                document.forms[0].elements["cs0" + x].value = document.forms[0].elements["SAno" + x].value;
                document.forms[0].elements["cf0" + x].value = document.forms[0].elements["CuotaFinanciamiento"].value;
                document.forms[0].elements["tp0" + x].value = TransformCurrency(cf * 1.0 + TransformNumber(document.forms[0].elements["SAno" + x].value) * 1.0);
            } else {
                document.forms[0].elements["cs0" + x].value = "";
                document.forms[0].elements["cf0" + x].value = "";
                document.forms[0].elements["tp0" + x].value = "";
            }
        }

        if (document.forms["CalcForm"].elements["ExtraPay"].value != "") {
            document.forms["CalcForm"].elements["ExtraPay"].value = TransformCurrency(document.forms["CalcForm"].elements["ExtraPay"].value);
            document.forms["CalcForm"].elements["ExtraCuota"].value = TransformCurrency(Math.round((parseFloat(TransformNumber(document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value)) + parseFloat(TransformNumber(document.forms["CalcForm"].elements["ExtraPay"].value))) * 100) / 100);

            var pos = 0;
            //for(;pos<4;pos++)
            for (; pos < 3; pos++)
                if (document.forms["CalcForm"].elements["Extra" + (pos + 2)].checked == true)
                    document.forms["CalcForm"].elements["ExtraCuota" + (pos + 2)].value = TransformCurrency(document.forms["CalcForm"].elements["ExtraCuota"].value);

        }
    }
}

function ChangeInteres() {
    if ((typeof(Page_ClientValidate) != 'function' || Page_ClientValidate())) {
        var PCCategory = parseFloat(TransformNumber(document.forms["CalcForm"].elements["SAno1"].value));

        var Interes = document.forms["CalcForm"].elements["txttasainteres"].value; //document.forms["CalcForm"].elements["TasaInteres"].value;

        //NEORIS: Se agrega función para plazos getSelectedNoCuota().
        var Month = getSelectedNoCuota();
        var Monto = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value);



        var temp = Math.pow(((parseFloat(Interes) + 1200) / 1200.00), Month);

        if (document.forms["CalcForm"].elements["ValorVehiculo"].value != "")
            document.forms["CalcForm"].elements["CuotaFinanciamientoTradicional"].value = TransformCurrency(Math.round(((Monto * Interes * temp) / ((temp - 1) * 1200) + PCCategory) * 100) / 100);
        //document.forms["CalcForm"].elements["CuotaFinanciamiento"].value = Math.round(((Monto * Interes *temp)/((temp - 1)*1200))*100)/100;
        if (Monto != "") {
            document.forms["CalcForm"].elements["CuotaFinanciamiento"].value = TransformCurrency(Math.round(((Monto * Interes * temp) / ((temp - 1) * 1200)) * 100) / 100);
            document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value = TransformCurrency(Math.round((PCCategory + parseFloat(TransformNumber(document.forms["CalcForm"].elements["CuotaFinanciamiento"].value))) * 100) / 100);
            document.forms["CalcForm"].elements["Diferencia"].value = TransformCurrency(Math.round((TransformNumber(document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value) - TransformNumber(document.forms["CalcForm"].elements["CuotaFinanciamientoTradicional"].value)) * 100) / 100);
        }

        ChangeExtraPay();
    }
}

function ChangeCategory() {
    if ((typeof(Page_ClientValidate) != 'function' || Page_ClientValidate())) {
        var PCCategory = 0;
        var valorVehiculo = TransformNumber(document.forms["CalcForm"].elements["ValorVehiculo"].value);
        var pos = 2;

        if (tipo != 2) {
            switch (document.forms["CalcForm"].elements["Categoria"].value) {
                case '1':
                    PCCategory = Math.round(valorVehiculo * (valorVehiculo <= precioMaximo1 ? newLightN1 : (valorVehiculo <= precioMaximo2 ? newLightN2 : (valorVehiculo <= precioMaximo3 ? newLightN3 : newLightN4))) / 1200);
                    break;
                case '2':
                    PCCategory = Math.round(valorVehiculo * (valorVehiculo <= precioMaximo1 ? newHeavyN1 : (valorVehiculo <= precioMaximo2 ? newHeavyN2 : (valorVehiculo <= precioMaximo3 ? newHeavyN3 : newHeavyN4))) / 1200);
                    break;
                case '3':
                    PCCategory = Math.round(valorVehiculo * (valorVehiculo <= precioMaximo1 ? newVanN1 : (valorVehiculo <= precioMaximo2 ? newVanN2 : (valorVehiculo <= precioMaximo3 ? newVanN3 : newVanN4))) / 1200);
                    break;
                case '4':
                    PCCategory = Math.round(valorVehiculo * (valorVehiculo <= precioMaximo1 ? newJeepetaN1 : (valorVehiculo <= precioMaximo2 ? newJeepetaN2 : (valorVehiculo <= precioMaximo3 ? newJeepetaN3 : newJeepetaN4))) / 1200);
                    break;
            }
        } else {
            switch (document.forms["CalcForm"].elements["Categoria"].value) {
                case '1':
                    PCCategory = Math.round(valorVehiculo * (valorVehiculo <= precioMaximo1 ? usedLightN1 : (valorVehiculo <= precioMaximo2 ? usedLightN2 : (valorVehiculo <= precioMaximo3 ? usedLightN3 : usedLightN4))) / 1200);
                    break;
                case '2':
                    PCCategory = Math.round(valorVehiculo * (valorVehiculo <= precioMaximo1 ? usedHeavyN1 : (valorVehiculo <= precioMaximo2 ? usedHeavyN2 : (valorVehiculo <= precioMaximo3 ? usedHeavyN3 : usedHeavyN4))) / 1200);
                    break;
                case '3':
                    PCCategory = Math.round(valorVehiculo * (valorVehiculo <= precioMaximo1 ? usedVanN1 : (valorVehiculo <= precioMaximo2 ? usedVanN2 : (valorVehiculo <= precioMaximo3 ? usedVanN3 : usedVanN4))) / 1200);
                    break;
                case '4':
                    PCCategory = Math.round(valorVehiculo * (valorVehiculo <= precioMaximo1 ? usedJeepetaN1 : (valorVehiculo <= precioMaximo2 ? usedJeepetaN2 : (valorVehiculo <= precioMaximo3 ? usedJeepetaN3 : usedJeepetaN4))) / 1200);
                    break;
            }
        }
        document.forms["CalcForm"].elements["SAno1"].value = TransformCurrency(PCCategory);
        /*			for(;pos<6;pos++)
                        document.forms["CalcForm"].elements["SAno" + pos].value = TransformCurrency(Math.round(TransformNumber(document.forms["CalcForm"].elements["SAno" + (pos -1)].value) * 0.85));
        */

        ChangeInteres();
    }
}


function getDateValue(fecha) {
    return (fecha.getMonth() + 1) + "/1" + "/" + fecha.getFullYear();
}

function StartDate() {
    document.forms["CalcForm"].elements["FechaDesembolso"].value = getDateValue(new Date());
    ChangeStartDate();
}

function ChangeDateSelector() {

    document.forms["CalcForm"].elements.selectedDate.value = 1;

    //var fecha = new Date(Date.parse(document.forms["CalcForm"].elements["DateSelector"].options[document.forms["CalcForm"].elements["DateSelector"].selectedIndex].innerText));

    var fecha = new Date(Date.parse(document.forms["CalcForm"].elements["DateSelector"].value));

    var pos = 0;
    //for(;pos<4;pos++){
    for (; pos < 3; pos++) {
        fecha.setFullYear(fecha.getFullYear() + 1);

        document.forms["CalcForm"].elements["DateSelector" + (pos + 2)].value = FormatDate(fecha);
    }
    ChangeExtraPay();
    RemoveRow();
}

function ChangeStartDate() {
    var fecha = new Date(document.forms["CalcForm"].elements["FechaDesembolso"].value);
    var init = fecha.getMonth();


    //NEORIS: Se agrega función para plazos getSelectedNoCuota().
    var end = init + parseInt(getSelectedNoCuota(), 10);
    var oOption;
    var count;

    for (count = document.forms["CalcForm"].elements["DateSelector"].options.length; count >= 0; count--)
        document.forms["CalcForm"].elements["DateSelector"].remove(count);

    count = 0;
    var k = 0;
    for (; init < end; init++) {

        fecha.setMonth(init % 12 + 1, 25);
        //oOption = document.createElement("OPTION");
        oOption = new Option(FormatDate(fecha), getDateValue(fecha));
        k = document.forms["CalcForm"].elements["DateSelector"].options.length;
        document.forms["CalcForm"].elements["DateSelector"].options[k] = oOption;

        //oOption.Value = getDateValue(fecha);//count++;
        //oOption.innerText = FormatDate(fecha);

    }
    document.forms["CalcForm"].elements["DateSelector"].selectedIndex = 0;
    // debugger;
    document.forms["CalcForm"].elements["FechaCancelacion"].value = getDateValue(fecha);

    ChangeDateSelector();
    return getDateValue(fecha);

}

function RemoveRow() {
    var startFecha = new Date(Date.parse(document.forms["CalcForm"].elements["FechaDesembolso"].value));
    var endFecha = new Date(Date.parse(document.forms["CalcForm"].elements["DateSelector"].options[document.forms["CalcForm"].elements["DateSelector"].selectedIndex].value));
    var m = (endFecha.getFullYear() - startFecha.getFullYear()) * 12 + (endFecha.getMonth() - startFecha.getMonth());

    //NEORIS: Se agrega función para plazos getSelectedNoCuota().
    var index = (getSelectedNoCuota() - m + 1) / 13 + 2;
    var n = getObj("Table6").rows.length;
    var init = 3;
    //for(;init < n;)
    for (; init < n;)
        if (init > index)
            getObj("Table6").rows[init++].style.visibility = "hidden";
        else
            getObj("Table6").rows[init++].style.visibility = "visible";
        //ChangeStartDate();
    ChangeInteres();

    //NEORIS: Se agrega función para plazos getSelectedNoCuota().
    index = getSelectedNoCuota() / 13 + 5;
    // n = getObj("Table4").rows.length;
    // init = 6;
    // for (; init < n;)
    //     if (init > index)
    //         getObj("Table4").rows[init++].style.visibility = "hidden";
    //     else
    //         getObj("Table4").rows[init++].style.visibility = "visible";
}

function showDetalleResumido() {
    var o;
    if (document.getElementById) {
        o = document.getElementById("DetalleResumido");
        o.style.display = o.style.display == "none" ? "block" : "none";

    } else if (document.all) {
        o = document.all("DetalleResumido");
        o.style.display = o.style.display == "none" ? "block" : "none";
    }
}


loadpage();