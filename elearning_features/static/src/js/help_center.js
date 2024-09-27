/** @odoo-module **/

import { registry } from "@web/core/registry";
import sAnimation from "@website/js/content/snippets.animation";


sAnimation.registry.OdooWebsiteSearchSuggestion = sAnimation.Class.extend({
    //animation.registry.OdooWebsiteSearchSuggestion = animation.Class.extend({
    selector: ".fad_search_box",
    start: function () {
        var self = this;
        this.$target.attr("autocomplete", "off");
        this.$target.parent().addClass("typeahead__container");


        this.$target.typeahead({
            minLength: 3,
            maxItem: 10,
            delay: 200,
            order: "asc",
            hint: true,
            dynamic: true,
            display: ["product", "faq"],
            maxItemPerGroup: 20,
            template: '<span>' +
                '<span>{{product}}</span> <span hidden>{{faq}}</span>' +
                '</span>',
            emptyTemplate: '<span>' +
                '<span>No se encuentra coincidencia</span>' +
                '</span>',

            source: {
                product: {url: [{type: "GET", url: "/search/faqs", data: {query: "{{query}}"},}, "data.product"]},

            },
            callback: {
                onClick: function (node, a, item, event) {

                    event.preventDefault();
                    this.hideLayout();

                    node.val(item.product);
                    node.blur();


                    $('html,body').animate({
                            scrollTop: ($('.faq-' + item.id).offset().top - 150)
                        },
                        'fast');


                },

                onResult(node, query, result, resultCount, resultCountPerGroup) {

                    // debugger;
                }

            },
        });


    },


    callback: {
        onClickAfter: function (node, a, item, event) {

            event.preventDefault;
            // debugger;

            // href key gets added inside item from options.href configuration
            alert(item.href);

        },
        onEnter: function (node, a, item, event) {

            event.preventDefault;
            // debugger;

            // href key gets added inside item from options.href configuration
            alert(item.href);

        },

        onClickBefore: function (node, a, item, event) {

            event.preventDefault;
            // debugger;

            // href key gets added inside item from options.href configuration
            alert(item.href);

        }
    },
    debug: false

});

