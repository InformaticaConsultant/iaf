odoo.define('website_form_validation.password_widget', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    //var base = require('web_editor.base');
    //var animation = require('web_editor.snippets.animation');
    var sAnimation = require('website.content.snippets.animation');

    var qweb = core.qweb;
    var _t = core._t;

    var ajax = require('web.ajax');
    sAnimation.registry.OdooWebsitePasswordWidget = sAnimation.Class.extend({
        selector: "#password_singup",
        start: function() {
            var self = this;

            this.$target.passtrength({
                passwordToggle: true,
                eyeImg: "/website_form_validation/static/src/img/eye.svg", // toggle icon
                tooltip: true,
                textWeak: "Débil",
                textMedium: "Media",
                textStrong: "Fuerte",
                textVeryStrong: "Muy Fuerte",
            });
        },
        debug: true

    });


});;