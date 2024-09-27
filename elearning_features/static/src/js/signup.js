/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
console.log('cargaaa')
publicWidget.registry.SignUpForm = publicWidget.Widget.extend({
    selector: '.oe_signup_form',
    events: {
        'submit': '_onSubmit',
    },

    init: function () {
            console.log('llamado al intit signup')
            this._super.apply(this, arguments);
            $('#login-user_type').on('change', function(e) {
                var value = $(this).val();
                var $cedula = $('#cedula');
                var $field_identification = $('.field-identification');
                var $label_passport = $('#label_passport');
                var $label_cedula = $('#label_cedula');
                $cedula.val('');

                if(value === 'adult'){

                    $field_identification.show();
                    $label_passport.hide();
                    $label_cedula.show();
                    $cedula.attr('required', true);
                    $cedula.attr('placeholder', 'Cédula');
                    $cedula.attr('maxlength', 11);
                    $cedula.attr('minlength', 11);
                    $cedula.attr('onkeypress', 'return onlyNumberKey(event)');


                }else if(value === 'foreign'){

                    $field_identification.show();
                    $label_passport.show();
                    $label_cedula.hide();
                    $cedula.attr('required', true);
                    $cedula.attr('placeholder', 'Pasaporte');
                    $cedula.attr('maxlength', 20);
                    $cedula.attr('minlength', 1);
                    $cedula.attr('onkeypress', '');

                }else{
                    $field_identification.hide();
                    $cedula.attr('required', false);
                    $cedula.attr('onkeypress', '');

                }

            });
        },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onSubmit: function () {
         console.log('sdsadadadadadsada')
        var $btn = this.$('.oe_login_buttons > button[type="submit"]');
        $btn.attr('disabled', 'disabled');
        $btn.prepend('<i class="fa fa-refresh fa-spin"/> ');
    },
});