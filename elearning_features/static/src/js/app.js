jQuery(document).ready(function() {

    // Menu en movil
    let hideMenu = false;
    jQuery("#main-movil .fa-bars").on("click", function() {
        jQuery(".movil-main-menu").toggle();
        hideMenu = !hideMenu;
    });
    document.addEventListener('scroll', () => {
        if (hideMenu) {
            jQuery(".movil-main-menu").toggle();
            hideMenu = false;
            console.log("Entró");
        }
    })

    // POPUP en la pagina de cursos
    jQuery(".popup .cerrar ").on("click", function() {
        jQuery(".popup").hide();
    });

    // Toggle dropdown del menu principal
    jQuery("nav.menu .container .main-menu #tools").on("click", function($event) {
        jQuery("nav.menu .container .main-menu #tools .dropdown").fadeToggle("slow");
    });

    // active de las opciones del menu principal
    jQuery("nav.menu .container .main-menu li *").on("click", function($event) {
        jQuery(".active").removeClass("active");
        jQuery($event.target).addClass("active");
    });

    // Dropdown del perfil de usuario
    let isHide = true;
    jQuery(".call-action").on("click", function() {
        let propertyValue = isHide ? 'block' : 'none';
        jQuery(".call-action .dropdown").css("display", propertyValue);
        jQuery("nav.menu .container .movil .movil-main-menu li .dropdown").css("display", propertyValue);
        isHide = !isHide;
    });
    document.addEventListener('scroll', () => {
        if (!isHide) {
            let propertyValue = isHide ? 'block' : 'none';
            jQuery(".call-action .dropdown").css("display", propertyValue);
            jQuery("nav.menu .container .movil .movil-main-menu li .dropdown").css("display", propertyValue);
            isHide = true;
        }
    })

});