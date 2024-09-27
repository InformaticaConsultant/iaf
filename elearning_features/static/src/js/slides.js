odoo.define('elearning_features.slides', function (require) {
    'use strict';

    var Quiz = require('website_slides.quiz');

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

    return Quiz;
});