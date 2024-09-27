/** @odoo-module **/

import {Component, useState, onMounted, onWillDestroy, useRef} from '@odoo/owl';
import {useService} from '@web/core/utils/hooks';
import {registry} from "@web/core/registry";
import {xml} from "@odoo/owl";

export class WebsitePodcastSearch extends Component {
    // Define las propiedades del componente
    setup() {
        this.state = useState({
            searchTerm: "",
            searchType: "",
            podcasts: [],
            noResults: false,
            loading: false,
            offset: 0,
            limit: 8,
        });
        this.search_type_ref = useRef('search_type_ref')
        this.search_input_ref = useRef('search_input_ref')
        this.scrollService = useService("scroller");
        this.rpc = useService("rpc")
        this.doneTypingInterval = 500;
        this.typingTimer = 0;


        // Configura el manejador de eventos de scroll para carga infinita
        //this.scrollService.onScroll(this.handleScroll.bind(this));
    }

    _onInput(ev) {
        var self = this;
        clearTimeout(this.typingTimer);
        self.typingTimer = setTimeout(async function() {
            self.state.offset = 0;  // Reset offset when a new search is made
            await self._searchInput();
        }, self.doneTypingInterval);
    }

    async _searchInput() {
        this.state.offset = 0;
        var search_type_el = this.search_type_ref.el.value
        var search_input_el = this.search_input_ref.el.value
        var $spinner = $('#podcast_spinner');
        var $no_results = $('#podcast_no_results');
        var $podcast_list = $('#podcast_list');

        $spinner.removeClass('d-none');

        const result = await this.rpc('/podcast/search', {
            search_term: search_input_el,
            search_type: search_type_el,
        });

        if (result[1] === 0 && this.state.offset === 0) {
            $no_results.removeClass('d-none');

        } else {
            $no_results.addClass('d-none');

        }

        if (this.state.offset === 0) {
            $podcast_list.html(result[0]);

        } else if (result[1] > 0) {
            // append only when there are more results
            var $parseHTML = $.parseHTML(result[0]);
            $podcast_list.append($parseHTML);

        }
        // Increment the offset by the limit for the next search.
        this.state.offset += this.state.limit;
        $spinner.addClass('d-none');
    }



    async handleSearch() {
        this.state.loading = true;

        try {
            const result = await this.rpc({
                route: "/podcast/search",
                params: {
                    search_term: this.state.searchTerm,
                    search_type: this.state.searchType,
                    offset: this.state.offset,
                    limit: this.state.limit,
                },
            });

            if (this.state.offset === 0) {
                this.state.podcasts = result[0];
            } else {
                this.state.podcasts.push(...result[0]);
            }

            this.state.noResults = result[1] === 0 && this.state.offset === 0;
            this.state.offset += this.state.limit;

        } catch (error) {
            console.error("An error occurred during podcast search:", error);
        } finally {
            this.state.loading = false;
        }
    }

     _onSearchFormSubmit(ev) {
        ev.preventDefault();
        this.state.offset = 0;
        this._searchInput();
    }
}

WebsitePodcastSearch.template = "website_podcast.WebsitePodcastSearch";
registry.category("public_components").add("website_podcast.WebsitePodcastSearch", WebsitePodcastSearch);

