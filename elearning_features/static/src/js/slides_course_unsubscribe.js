odoo.define('web_notify.WebsiteClient', function(require) {
    "use strict";

    var unsubscribe_modal = require('website_slides.unsubscribe_modal');
    var join_widget = require('website_slides.course.join.widget');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;
    var MESSAGE_NOTIFY = {
        type: "success",
        title: "Cursos/Workshops",
        message: "",
        sticky: false,

    }

    unsubscribe_modal.SlideUnsubscribeDialog.include({
        init: function (parent, options) {
            this._super(parent, options);

            this._texts.titleSubscribe = "Suscribete"
            this._texts.titleUnsubscribe = "Cancelar suscripción"
            this._texts.titleLeaveCourse = "Abandonar el curso"

        },
         _resetModal: function () {
            this._texts.titleSubscribe = "Suscribete"
            this._texts.titleUnsubscribe = "Cancelar suscripción"
            this._texts.titleLeaveCourse = "Abandonar el curso"
            this._super();

        },
        _onClickLeaveCourseSubmit: function() {
            var self = this
            this._rpc({
                route: '/cursos/channel/leave',
                params: {
                    channel_id: this.channelID
                },
            }).then(function() {
                rpc.query({
                    model: 'slide.channel',
                    method: 'search_read',
                    args: [
                        [
                            ['id', '=', self.channelID]
                        ],
                        ['name']
                    ],
                }, {
                    timeout: 10000,
                }).then(function(response) {
                    let slide = response[0].name || "INDEFINIDO";
                    let message = `Se ha removido del curso o workshop : ${slide}, de manera exitosa! `
                    MESSAGE_NOTIFY.message = message;
                    self.call(
                        'notification', 'notify', MESSAGE_NOTIFY
                    );
                    setTimeout(function() {
                        window.location.reload();
                    }, 200);
                });

            });
        }
    });
    join_widget.courseJoinWidget.include({
        _onClickJoin: function(event) {

            var channelId = this.channelId || $(event.currentTarget).data('channel-id');
            var self = this;
            this._rpc({
                route: '/cursos/channel/join',
                params: {
                    channel_id: channelId,
                },
            }).then(function(data) {
                if (!data.error) {


                    rpc.query({
                        model: 'slide.channel',
                        method: 'search_read',
                        args: [
                            [
                                ['id', '=', channelId]
                            ],
                            ['name']
                        ],
                    }, {
                        timeout: 10000,
                    }).then(function(response) {
                        let slide = response[0].name || "INDEFINIDO";

                        let message = `Se ha inscripto al curso o workshop : ${slide}, de manera exitosa! `
                        MESSAGE_NOTIFY.message = message;
                        self.call(
                            'notification', 'notify', MESSAGE_NOTIFY
                        );

                        setTimeout(function() {
                            window.location.reload();
                        }, 200);

                    });

                    // location.reload();
                } else {
                    if (data.error === 'public_user') {
                        var message = _t('Please <a href="/web/login?redirect=%s">login</a> to join this course');
                        var signupAllowed = data.error_signup_allowed || false;
                        if (signupAllowed) {
                            message = _t('Please <a href="/web/signup?redirect=%s">create an account</a> to join this course');
                        }
                        self._popoverAlert(self.$el, _.str.sprintf(message, (document.URL)));
                    } else if (data.error === 'join_done') {
                        self._popoverAlert(self.$el, _t('Ya esta suscrito a este curso'));
                    } else {
                        self._popoverAlert(self.$el, _t('Unknown error'));
                    }
                }
            });
        }
    });

});

function goBackAcademia() {
    window.history.back();
}