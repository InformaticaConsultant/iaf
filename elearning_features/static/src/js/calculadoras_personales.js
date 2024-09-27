 /* Personal Loan Calculator
                                                                                                                                                                                                                                                                                                                                                                                                                                                                          http://66.98.67.3/SolicitudesBPD/Productos/CalcPrestamo.aspx
                                                                                                                                                                                                                                                                                                                                                                                                                                                                         Taken from source file
                                                                                                                                                                                                                                                                                                                                                                                                                                                                        */
 //NEORIS: Se agrega variable tipo para saber que tipo de préstamo se va a calcular

 //  $.noConflict();
    console.trace()
 var tipo = getUrlVars()["tipo"];
 var factor, montoasegurarH;

 function loadpage() {
     getParameterTerm();
     StartDate();
 }

 //NEORIS: Se agrega función para que en el campo de tasa de interés solo se capturen datos numéricos
 function valida(e) {
     tecla = (document.all) ? e.keyCode : e.which;

     if (tecla == 8) {
         return true;
     }

     patron = /[0-9.]/;
     tecla_final = String.fromCharCode(tecla);
     return patron.test(tecla_final);
 }

 function getObj(objid) {
     if (document.getElementById)
         return document.getElementById(objid);
     else if (document.all)
         return document.all(objid);
     return null;
 }

 var months = new Array("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre");

 function PC(op, div) {

     return Math.round(op * 1000 / div) / 10;
 }

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

 //NEORIS. Función para leer parámetros de la tabla Lista paramétrica
 function getParameterTerm() {
     var spUrl = location.protocol + "//" + location.hostname + "/_api/web/lists/getbytitle('ListParametrica')/items?$filter=Title eq 'values'";

     $.ajax({
         url: spUrl,
         method: "GET",
         headers: {
             "Accept": "application/json; odata=verbose"
         },
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

                 //Obteniendo el plazo.    
                 var aResult = data.d.results[0];

                 if (aResult.loanAmountPerson != null) {
                     factor = aResult.loanAmountPerson;
                 }

                 if (factor == "" || factor == undefined) {
                     factor = 0.00065;
                 }

                 if (aResult.amountToInsurePerson != null) {
                     montoasegurarH = aResult.amountToInsurePerson;
                 }

                 if (montoasegurarH == "" || montoasegurarH == undefined) {
                     montoasegurarH = 3000000;
                 }
                 if (tipo <= 4) {
                     getObj("Seguro1").innerHTML = "Aplica solo hasta RD$" + TransformCurrency(montoasegurarH);
                 } else {
                     getObj("SeguroDeudor2").style.display = 'none';
                     getObj("SeguroDeudor1").style.display = 'none';
                 }

                 if (tipo == 2 || tipo == 3) {
                     getObj("tituloCalculadora").innerHTML = "Calculadora de préstamos";
                 } else {
                     getObj("tituloCalculadora").innerHTML = "Calculadora de préstamos personales";
                 }
             }
         }

     );
 }

 function ChangeMontoVehiculo() {
     var valorVehiculo = TransformNumber(document.forms["CalcForm"].elements["ValorVehiculo"].value);

     if (valorVehiculo <= 0) {
         alert("El monto del préstamo no debe ir vacio y ser mayor que cero.");
         //document.forms["CalcForm"].elements["ValorVehiculo"].focus();
         //document.location.reload();
         return;
     }

     if ((typeof(Page_ClientValidate) != 'function' || Page_ClientValidate())) {
         //console.log("Entro");

         document.forms["CalcForm"].elements["MontoFinanciar"].value = valorVehiculo;
         var valorFinanciar = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciar"].value);
         var valorFinanciamiento = valorVehiculo; //valorFinanciar > valorVehiculo * 0.90 ? valorVehiculo * 0.90 : valorFinanciar;

         document.forms["CalcForm"].elements["InicialPagar"].value = TransformCurrency(valorVehiculo - valorFinanciamiento);
         document.forms["CalcForm"].elements["MontoFinanciamiento"].value = TransformCurrency(valorFinanciamiento);
         document.forms["CalcForm"].elements["PCInicialPagar"].value = PC(TransformNumber(document.forms["CalcForm"].elements["InicialPagar"].value), valorVehiculo) + " %";
         document.forms["CalcForm"].elements["PCMontoFinanciar"].value = PC(valorFinanciar, valorVehiculo) + " %";
         document.forms["CalcForm"].elements["PCMontoFinanciamiento"].value = PC(valorFinanciamiento, valorVehiculo) + " %";
         document.forms["CalcForm"].elements["GastosInscripcion"].value = "0"; // TransformCurrency(valorVehiculo > 0 ? (valorVehiculo <= 300000 ? 4000 :  (valorVehiculo <= 700000 ? 6000 : 8000)):0);
         document.forms["CalcForm"].elements["LimiteAnualFinanciamiento"].value = TransformCurrency(PC(valorFinanciamiento, 1000));
         document.forms["CalcForm"].elements["PagoInmediato"].value = TransformCurrency(parseFloat(TransformNumber(document.forms["CalcForm"].elements["InicialPagar"].value)) + parseFloat(TransformNumber(document.forms["CalcForm"].elements["GastosInscripcion"].value)));
         document.forms["CalcForm"].elements["MontoFinanciar"].value = TransformCurrency(document.forms["CalcForm"].elements["MontoFinanciar"].value);
         document.forms["CalcForm"].elements["ValorVehiculo"].value = TransformCurrency(document.forms["CalcForm"].elements["ValorVehiculo"].value);
         factor = 0.00075;
         montoasegurarH = 3000000
         if (true) {

             if (valorFinanciamiento <= montoasegurarH) {
                 document.forms["CalcForm"].elements["SeguroDeudor1"].value = TransformCurrency(factor * document.forms["CalcForm"].elements["NoCuotas"].value * valorFinanciamiento);
             } else {
                 document.forms["CalcForm"].elements["SeguroDeudor1"].value = TransformCurrency(factor * document.forms["CalcForm"].elements["NoCuotas"].value * montoasegurarH);
             }
         }
         ChangeCategory();

         if (document.forms["CalcForm"].elements["MontoFinanciamiento"].value == "0.00")
             document.forms["CalcForm"].elements["MontoFinanciamiento"].value = "";

         if (document.forms["CalcForm"].elements["MontoFinanciar"].value == "0.00")
             document.forms["CalcForm"].elements["MontoFinanciar"].value = "";
     }
 }

 function ChangeExtraPay() {
     if ((typeof(Page_ClientValidate) != 'function' || Page_ClientValidate()) && document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value != "") {
         var startFecha = new Date(Date.parse(document.forms["CalcForm"].elements["FechaDesembolso"].value));
         var endFecha = new Date(Date.parse(document.forms["CalcForm2"].elements["DateSelector"].options[document.forms["CalcForm2"].elements["DateSelector"].selectedIndex].value));
         var Interes = document.forms["CalcForm"].elements["TasaInteres"].value;

         var m = (endFecha.getFullYear() - startFecha.getFullYear()) * 12 + (endFecha.getMonth() - startFecha.getMonth());
         var x = Math.pow(((parseFloat(Interes) + 1200) / 1200.00), m);
         var Monto = parseFloat(TransformNumber(document.forms["CalcForm"].elements["MontoFinanciamiento"].value));
         var PCCategory = parseFloat(TransformNumber(document.forms["CalcForm"].elements["SAno1"].value));

         if (document.forms["CalcForm"].elements["MontoFinanciamiento"].value == "" || document.forms["CalcForm2"].elements["ExtraPay"].value == "" || parseFloat(document.forms["CalcForm2"].elements["ExtraPay"].value) == 0)
             document.forms["CalcForm2"].elements["ExtraPay"].value = "";
         if (document.forms["CalcForm2"].elements["ExtraPay"].value == "")
             document.forms["CalcForm2"].elements["ExtraCuota"].value = "";
         else {
             //document.forms["CalcForm"].elements["ExtraCuota"].value = parseFloat(document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value) + parseFloat(document.forms["CalcForm"].elements["ExtraPay"].value);	
             //Monto -= parseFloat(document.forms["CalcForm"].elements["ExtraPay"].value);
             Monto -= Math.round((TransformNumber(document.forms["CalcForm2"].elements["ExtraPay"].value) / x) * 100) / 100;
         }

         var pos = 0;
         //for(;pos<4;pos++){
         for (; pos < 3; pos++) {

             if (document.forms["CalcForm2"].elements["Extra" + (pos + 2)].checked == true && document.forms["CalcForm"].elements["MontoFinanciamiento"].value != "") {
                 document.forms["CalcForm2"].elements["ExtraPay" + (pos + 2)].value = TransformCurrency(document.forms["CalcForm2"].elements["ExtraPay"].value);
                 //document.all["ExtraCuota" + (pos + 2)].value = document.forms["CalcForm"].elements["ExtraCuota"].value;
                 //endFecha = new Date(Date.parse(document.all["DateSelector" + (pos +2)].Value));
                 endFecha = new Date(Date.parse(document.forms["CalcForm2"].elements["DateSelector"].options[document.forms["CalcForm2"].elements["DateSelector"].selectedIndex].value));
                 endFecha.setFullYear(endFecha.getFullYear() + pos + 1);

                 m = (endFecha.getFullYear() - startFecha.getFullYear()) * 12 + (endFecha.getMonth() - startFecha.getMonth());
                 x = Math.pow(((parseFloat(Interes) + 1200) / 1200.00), m);
                 Monto -= Math.round((TransformNumber(document.forms["CalcForm2"].elements["ExtraPay"].value) / x) * 100) / 100;
             } else {
                 document.forms["CalcForm2"].elements["Extra" + (pos + 2)].checked = false;
                 document.forms["CalcForm2"].elements["ExtraPay" + (pos + 2)].value = "";
                 document.forms["CalcForm2"].elements["ExtraCuota" + (pos + 2)].value = "";
             }
         }


         var Month = document.forms["CalcForm"].elements["NoCuotas"].value;
         var temp = Math.pow(((parseFloat(Interes) + 1200) / 1200.00), Month);

         if (document.forms["CalcForm"].elements["MontoFinanciamiento"].value != "") {
             document.forms["CalcForm"].elements["CuotaFinanciamiento"].value = TransformCurrency(Math.round(((Monto * Interes * temp) / ((temp - 1) * 1200)) * 100) / 100);
             document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value = TransformCurrency(Math.round((PCCategory + parseFloat(TransformNumber(document.forms["CalcForm"].elements["CuotaFinanciamiento"].value))) * 100) / 100);
             document.forms["CalcForm"].elements["Diferencia"].value = TransformCurrency(Math.round((TransformNumber(document.forms["CalcForm"].elements["CuotaFinanciamientoTradicional"].value) - TransformNumber(document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value)) * 100) / 100);
         } else {
             document.forms["CalcForm"].elements["CuotaFinanciamiento"].value = "";
             document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value = "";
             document.forms["CalcForm"].elements["Diferencia"].value = "";
         }

         //document.forms["CalcForm"].elements["ExtraCuota"].value = parseFloat(document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value) + parseFloat(document.forms["CalcForm"].elements["ExtraPay"].value);	


         var cf = TransformNumber(document.forms["CalcForm"].elements["CuotaFinanciamiento"].value);
         var seg;
         var m = Month / 12;
         for (var x = 1; x < 6; x++) {
             seg = TransformNumber(document.forms["CalcForm"].elements["SAno" + x].value)
             if (x < m + 1) {
                 // console.log("alex");

                 // console.log(document.getElementById("SAno" + x).value);
                 // console.log(document.getElementById("cs0" + x));

                 document.getElementById("cs0" + x).value = document.getElementById("SAno" + x).value;
                 document.forms["CalcForm2"].elements["cf0" + x].value = document.forms["CalcForm"].elements["CuotaFinanciamiento"].value;
                 document.forms["CalcForm2"].elements["tp0" + x].value = TransformCurrency(cf * 1.0 + TransformNumber(document.forms["CalcForm"].elements["SAno" + x].value) * 1.0);
             } else {
                 document.forms["CalcForm2"].elements["cs0" + x].value = "";
                 document.forms["CalcForm2"].elements["cf0" + x].value = "";
                 document.forms["CalcForm2"].elements["tp0" + x].value = "";
             }
         }

         if (document.forms["CalcForm2"].elements["ExtraPay"].value != "") {
             document.forms["CalcForm2"].elements["ExtraPay"].value = TransformCurrency(document.forms["CalcForm2"].elements["ExtraPay"].value);
             document.forms["CalcForm2"].elements["ExtraCuota"].value = TransformCurrency(Math.round((parseFloat(TransformNumber(document.forms["CalcForm"].elements["CuotaPagosExtraordinarios"].value)) + parseFloat(TransformNumber(document.forms["CalcForm2"].elements["ExtraPay"].value))) * 100) / 100);

             var pos = 0;
             //for(;pos<4;pos++)
             for (; pos < 3; pos++)
                 if (document.forms["CalcForm2"].elements["Extra" + (pos + 2)].checked == true)
                     document.forms["CalcForm2"].elements["ExtraCuota" + (pos + 2)].value = TransformCurrency(document.forms["CalcForm2"].elements["ExtraCuota"].value);

         }
     }
 }

 function ChangeInteres() {
     if ((typeof(Page_ClientValidate) != 'function' || Page_ClientValidate())) {
         var PCCategory = parseFloat(TransformNumber(document.forms["CalcForm"].elements["SAno1"].value));

         var Interes = document.forms["CalcForm"].elements["TasaInteres"].value;
         var Month = document.forms["CalcForm"].elements["NoCuotas"].value;
         var Monto = TransformNumber(document.forms["CalcForm"].elements["MontoFinanciamiento"].value);



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

         switch (document.forms["CalcForm"].elements["Categoria"].value) {
             case '1':
                 PCCategory = 0; //Math.round(valorVehiculo * (valorVehiculo <= 199999 ? 7.9 : ( valorVehiculo <= 349999 ? 7.0 : (valorVehiculo <= 499999 ? 6.6 : (valorVehiculo <= 699999 ? 6.3 : 6.0))))/1200);
                 break;
             case '2':
                 PCCategory = 0; //Math.round(valorVehiculo * (valorVehiculo <= 199999 ? 10.1 : ( valorVehiculo <= 349999 ? 8.9 : (valorVehiculo <= 499999 ? 8.4 : (valorVehiculo <= 699999 ? 8.0 : 7.7))))/1200);
                 break;
             case '3':
                 PCCategory = 0; //Math.round(valorVehiculo * (valorVehiculo <= 199999 ? 8.3 : ( valorVehiculo <= 349999 ? 7.3 : (valorVehiculo <= 499999 ? 6.9 : (valorVehiculo <= 699999 ? 6.6 : 6.3))))/1200);
                 break;

         }
         document.forms["CalcForm"].elements["SAno1"].value = TransformCurrency(PCCategory);
         for (; pos < 6; pos++)
             document.forms["CalcForm"].elements["SAno" + pos].value = TransformCurrency(Math.round(TransformNumber(document.forms["CalcForm"].elements["SAno" + (pos - 1)].value) * 0.85));

         ChangeInteres();
     }
 }

 function StartDate() {
     document.forms["CalcForm"].elements["FechaDesembolso"].value = getDateValue(new Date());
     ChangeStartDate();
 }

 function ChangeDateSelector() {

     document.forms["CalcForm"].elements.selectedDate.value = 1;

     //var fecha = new Date(Date.parse(document.forms["CalcForm"].elements["DateSelector"].options[document.forms["CalcForm"].elements["DateSelector"].selectedIndex].innerText));

     var fecha = new Date(Date.parse(document.forms["CalcForm2"].elements["DateSelector"].value));

     //  var fecha = new Date(Date.parse("06/23/2021"));
     //  debugger;

     var pos = 0;
     //for(;pos<4;pos++){
     for (; pos < 3; pos++) {
         fecha.setFullYear(fecha.getFullYear() + 1);

         document.forms["CalcForm2"].elements["DateSelector" + (pos + 2)].value = FormatDate(fecha);
     }
     ChangeExtraPay();
     RemoveRow();
 }

 function ChangeStartDate() {
     var valorVehiculo = TransformNumber(document.forms["CalcForm"].elements["ValorVehiculo"].value);
     var fecha = new Date(Date.parse(document.forms["CalcForm"].elements["FechaDesembolso"].value));
     //  debugger;
     var init = fecha.getMonth();
     var end = init + parseInt(document.forms["CalcForm"].elements["NoCuotas"].value, 10);
     var oOption;
     var count;

     for (count = document.forms["CalcForm2"].elements["DateSelector"].options.length; count >= 0; count--)
         document.forms["CalcForm2"].elements["DateSelector"].remove(count);

     count = 0;
     var k = 0;
     for (; init < end; init++) {

         fecha.setMonth(init % 12 + 1, 25);
         //oOption = document.createElement("OPTION");
         oOption = new Option(FormatDate(fecha), getDateValue(fecha));
         k = document.forms["CalcForm2"].elements["DateSelector"].options.length;
         document.forms["CalcForm2"].elements["DateSelector"].options[k] = oOption;

         //oOption.Value = getDateValue(fecha);//count++;
         //oOption.innerText = FormatDate(fecha);

     }
     document.forms["CalcForm2"].elements["DateSelector"].selectedIndex = 0;
     document.forms["CalcForm"].elements["FechaCancelacion"].value = getDateValue(fecha);

     if (true) {
         document.forms["CalcForm"].elements["SeguroDeudor1"].value = TransformCurrency(factor * document.forms["CalcForm"].elements["NoCuotas"].value * valorVehiculo);
     }
     ChangeDateSelector();


 }

 function RemoveRow() {
     var startFecha = new Date(Date.parse(document.forms["CalcForm"].elements["FechaDesembolso"].value));
     var endFecha = new Date(Date.parse(document.forms["CalcForm2"].elements["DateSelector"].options[document.forms["CalcForm2"].elements["DateSelector"].selectedIndex].value));
     var m = (endFecha.getFullYear() - startFecha.getFullYear()) * 12 + (endFecha.getMonth() - startFecha.getMonth());
     var index = (document.forms["CalcForm"].elements["NoCuotas"].value - m + 1) / 13 + 2;
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

     index = document.forms["CalcForm"].elements["NoCuotas"].value / 13 + 5;
     n = getObj("Table4").rows.length;
     init = 6;
     for (; init < n;)
         if (init > index)
             getObj("Table4").rows[init++].style.visibility = "hidden";
         else
             getObj("Table4").rows[init++].style.visibility = "visible";
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


 window.addEventListener("pageshow", () => {
     jQuery("#categoria").val("Préstamos personales");
 });