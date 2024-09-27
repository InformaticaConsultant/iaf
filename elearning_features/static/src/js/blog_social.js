var shareWhatsapp = document.querySelectorAll(".shareWhatsapp");
var whatapp_btn = document.querySelector(".o_whatsapp");
var message = encodeURIComponent(window.location.href);
var ws_link = "https://api.whatsapp.com/send?text=" + message;

if (whatapp_btn) {

    whatapp_btn.setAttribute('href', ws_link);

    console.log("url encode: " + message)
    console.log("Link " + ws_link)

}