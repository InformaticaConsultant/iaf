odoo.define('website_podcast.podcast', function(require) {
    'use strict';

    var core = require('web.core');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');

    var _t = core._t;
    var QWeb = core.qweb;


    publicWidget.registry.WebsitePodcastSearch = Widget.extend({
        selector: '#podcast_search_form',
        events: {
            'submit': '_onSearchFormSubmit',
            'input input[id="search_term"]': '_onInput',
        },

        init: function () {
            this._super.apply(this, arguments);
            this.typingTimer;  // Timer identifier
            this.doneTypingInterval = 500;  // Time in ms. e.g. 0.5 seconds
            this.offset = 8;
            this.limit = 8;
        },

        start: function() {
            // TODO: Search scroll sometimes call twice
            this._super.apply(this, arguments);
            var self = this;
    
            $(window).on('scroll touchmove', function () {
                var st = $(this).scrollTop();
                if (st > self.lastScrollTop){
                    // downscroll code
                    if($(window).scrollTop() + $(window).height() == $(document).height()) {
                        self._search();
                    }
                }
                self.lastScrollTop = st;
            });
            

        },

        _onInput: function(ev) {
            var self = this;

            clearTimeout(this.typingTimer);
            this.typingTimer = setTimeout(function() {
                self.offset = 0;  // Reset offset when a new search is made
                self._search();
            }, self.doneTypingInterval);
        }, 

        _search: function() {
            var self = this;
            var search_term = this.$('input[id="search_term"]').val();
            var search_type = this.$('select[id="search_type"]').val();
            var $spinner = $('#podcast_spinner');
            var $no_results = $('#podcast_no_results');
            var $podcast_list = $('#podcast_list');

            $spinner.removeClass('d-none');
            ajax.jsonRpc('/podcast/search', 'call', {
                'search_term': search_term,
                'search_type': search_type,
                'offset': self.offset,
                'limit': self.limit
            }).then(function(data) {


                if (data[1] === 0 && self.offset === 0){
                    $no_results.removeClass('d-none');

                } else {
                    $no_results.addClass('d-none');

                }
                
                if (self.offset === 0) {
                    $podcast_list.html(data[0]);

                } else if (data[1] > 0) { 
                    // append only when there are more results 
                    var $parseHTML = $.parseHTML(data[0]);
                    $podcast_list.append($parseHTML);
                
                }
                // Increment the offset by the limit for the next search.
                self.offset += self.limit;
                $spinner.addClass('d-none');

            }).catch(function(error) {
                console.error("An error occurred:", error);
                $spinner.addClass('d-none');

            });;
        },

        _onSearchFormSubmit: function(ev) {
            ev.preventDefault();
            this.offset = 0;
            this._search();
        },

    });

    return publicWidget.registry.WebsitePodcastSearch;
});
