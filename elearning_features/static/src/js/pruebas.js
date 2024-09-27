
odoo.define('elearning_features.fullscreen', function (require) {
    'use strict';

    var Fullscreen = require('website_slides.fullscreen');
    var Quiz = require('website_slides.quiz');
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

    var findSlide = function (slideList, matcher) {
        var slideMatch = _.matcher(matcher);
        return _.find(slideList, slideMatch);
    };

    Fullscreen.include({
        _onChangeSlideRequest: function (ev) {
            var slideData = ev.data;
            let block_access = false;
            let block_name = "";

            var newSlide = findSlide(this.slides, {
                id: slideData.id,
                isQuiz: slideData.isQuiz || false,
            });

            for (let index = 0; index < this.slides.length; index++) {
                const slide = this.slides[index];
                if (newSlide.id === slide.id) {
                    break;
                }
                if (slide.required && !slide.completed) {
                    block_access = true;
                    block_name = slide.name
                }
            }

            if (block_access) {
                return this.call(
                    'notification', 'notify', {
                        type: 'danger',
                        title: 'Contenido requerido',
                        message: 'Debes completar el contenido anterior, antes de pasar al siguiente cápitulo',
                        sticky: false,
                    }
                );
                return
            } else {
                return this._super(ev);
            }
        },

        _renderSlide: function () {
            this._super.apply(this, arguments);
            var self = this;

            if (this.videoPlayer) {
                this.videoPlayer._onPlayerStateChange = function (event) {
                    var self = this;
                    if (self.slide.completed && event.data == YT.PlayerState.ENDED) {
                        if (this.slide.hasNext) {
                            this.trigger_up('slide_go_next');
                        } else {
                            this.player.playVideo();
                        }
                        return;
                    }
                    if (self.slide.completed) {
                        return;
                    }
                    if (event.data !== YT.PlayerState.ENDED) {
                        if (!event.target.getCurrentTime) {
                            return;
                        }

                        if (self.tid) {
                            clearInterval(self.tid);
                        }

                        self.currentVideoTime = event.target.getCurrentTime();
                        self.totalVideoTime = event.target.getDuration();
                        self.tid = setInterval(function () {
                            self.currentVideoTime += 1;
                            if (self.totalVideoTime && self.currentVideoTime > self.totalVideoTime - 30) {
                                clearInterval(self.tid);
                                if (!self.slide.hasQuestion && !self.slide.completed) {
                                    self.trigger_up('slide_to_complete', self.slide);
                                }
                            }
                        }, 1000);
                    } else {
                        if (self.tid) {
                            clearInterval(self.tid);
                        }
                        this.player = undefined;
                        if (this.slide.hasNext) {
                            this.trigger_up('slide_go_next');
                        }
                    }
                }

                var slide = this.get('slide');
                if (slide.type == "video" && slide.embedUrl && slide.embedUrl.includes('vimeo')) {
                    setTimeout(function () {
                        try {
                            var iframe = document.querySelector('iframe')
                            if (iframe) {
                                var slide = self.get('slide');
                                self.slide = slide
                                if (slide.type == "video" && slide.embedUrl && slide.embedUrl.includes('vimeo')) {
                                }else{
                                    return;
                                }

                                var player = new Vimeo.Player(iframe);
                                player.on('play', function () {
                                    console.log('Played the video');
                                });
    //                            player.getVideoTitle().then(function (title) {
    //                                console.log('title:', title);
    //                            });
    //
    //                            player.on('timeupdate', function (time) {
    //                                console.log(time);
    //                            });

                                player.on('pause', function () {
                                    var durationTime = 0;
                                    var currentTime = 0;

                                    player.getDuration().then(function (value) {
                                        durationTime = value;
                                        player.getCurrentTime().then(function (value) {
                                            currentTime = value;

                                            if (currentTime > durationTime - 30) {
                                                if (!self.slide.hasQuestion && !self.slide.completed) {
                                                    self.trigger_up('slide_to_complete', self.slide);
                                                    var slideVideo =  self.slide;

                                                    if (self.slide.hasNext) {
                                                        setTimeout(function () {
                                                            // debugger;
                                                            if(slideVideo == self.get('slide')){
                                                                self.trigger_up('slide_go_next');
                                                            }

                                                        }, 4000);
                                                    }
                                                }
                                            }
                                        })
                                    })
                                });
                            }
                        } catch (error) {
                            console.log("No es un video de vimeo");
                            console.log(error);
                        }
                    }, 5000);
                }
            }
        }
    });

    Quiz.extend({
        _renderSuccessModal: function () {
            var $modal = this.$('#slides_quiz_modal');
            if (!$modal.length) {
                this.$el.append(QWeb.render('slide.slide.quiz.finish', {'widget': this}));
                $modal = this.$('#slides_quiz_modal');
            }
            $modal.modal({
                'show': false,
            });
            $modal.on('hidden.bs.modal', function () {
                $modal.remove();
            });
        },

    });

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
                route: '/slides/channel/leave',
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
                route: '/slides/channel/join',
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

/*
setTimeout(function () {
    try {
        var self = this;
        var iframe = document.querySelector('iframe')
        if (iframe) {
            var slide_elemen = this.$(".o_wslides_lesson_aside_list_link.active")
            var slide_href = slide_elemen.attr('href');
            var divicion =  slide_href.split('-');
            var slide_id = divicion[divicion.length - 1]

            self.slide_id = slide_id
            if (slide_id) {
            }else{
                return;
            }

            var player = new Vimeo.Player(iframe);
            player.on('play', function () {
                console.log('Played the video');
            });
//                            player.getVideoTitle().then(function (title) {
//                                console.log('title:', title);
//                            });
//
//                            player.on('timeupdate', function (time) {
//                                console.log(time);
//                            });

            player.on('pause', function () {
                var durationTime = 0;
                var currentTime = 0;

                player.getDuration().then(function (value) {
                    durationTime = value;
                    player.getCurrentTime().then(function (value) {
                        currentTime = value;

                        if (currentTime > durationTime - 30) {

                           this.$.ajax({
                                url: '/cursos/curso/'+self.slide_id+'/set_completed',
                                method: "GET",
                                success: function(data) {
                                success_circle =  slide_elemen.find('i').eq(0);
                                success_circle.removeClass('fa-circle-o');
                                success_circle.removeClass('text-600');
                                success_circle.addClass('fa-check-circle');
                                success_circle.addClass('text-success ');
                                },
                                error: function(data) {
                                    console.log(data);
                                    //TODO:
                                }
                            });
                            // if (!self.slide.hasQuestion && !self.slide.completed) {
                            //     self.trigger_up('slide_to_complete', self.slide);

                            //     if (self.slide.hasNext) {
                            //         setTimeout(function () {
                            //             self.trigger_up('slide_go_next');

                            //         }, 4000);
                            //     }
                            // }
                        }
                    })
                })
            });
        }
    } catch (error) {
        console.log("No es un video de vimeo");
        console.log(error);
    }
}, 5000);*/
