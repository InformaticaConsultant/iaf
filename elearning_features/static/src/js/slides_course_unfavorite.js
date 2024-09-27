/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';
import { useService } from "@web/core/utils/hooks";
import { RPCError } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";

console.log('widget website slide teacher follow')
publicWidget.registry.WebsiteSlidesTeacherFollow = publicWidget.Widget.extend({
    selector: '.o_wslides_js_teacher_follow',
    events: {
        'click .o_wslides_js_teacher_follow_link': '_onClickFollow',
        'click .o_wslides_js_teacher_unfollow_link': '_onClickUnfollow',
    },

    /**
     * @override
     */
      init: function (parent, options) {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");

    },

    /**
     * @private
     * Muestra un popover de error.
     */
    _popoverAlert: function ($el, message) {
        $el.popover({
            trigger: 'focus',
            placement: 'bottom',
            container: 'body',
            html: true,
            content: function () {
                return message;
            }
        }).popover('show');
    },

    /**
     * @private
     * Maneja el evento de seguir al maestro.
     */
    _onClickFollow: function (event) {
        event.preventDefault();
        const channelId = $(event.currentTarget).data('channel-id');
        const partnerId = $(event.currentTarget).data('partner-id');
        const self = this;

        this.rpc('/cursos/channel/teacher/follow', {
                'channel_id': channelId,
                'partner_id': partnerId,
        }).then(function (data) {
            if (!data.error) {
                location.reload();
            } else {
                if (data.error === 'fail') {
                    self._popoverAlert(self.$el, _t('Error intentado asignarle como seguidor, intente de nuevo.'));
                }
            }
        });
    },

    /**
     * @private
     * Maneja el evento de dejar de seguir al maestro.
     */
    _onClickUnfollow: function (event) {
        event.preventDefault();
        const channelId = $(event.currentTarget).data('channel-id');
        const partnerId = $(event.currentTarget).data('partner-id');
        const self = this;

         this.rpc('/cursos/channel/teacher/unfollow', {
                'channel_id': channelId,
                'partner_id': partnerId,
        }).then(function (data) {
            if (!data.error) {
                location.reload();
            } else {
                if (data.error === 'fail') {
                    self._popoverAlert(self.$el, _t('Error intentado asignarle como seguidor, intente de nuevo.'));
                }
            }
        });
    },
});
