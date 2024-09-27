/** @odoo-module */
import { Notification } from "@web/core/notifications/notification";
import { patch } from "@web/core/utils/patch";

patch(Notification.prototype, {
    setup() {
        super.setup();
        this.props.type = {
            type: String,
            optional: true,
            validate: (t) => ["warning", "danger", "success", "info", "default"].includes(t),
        };
    },
});
