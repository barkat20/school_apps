/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ProgressBarField, progressBarField } from "@web/views/fields/progress_bar/progress_bar_field";
import { useEffect } from "@odoo/owl";

export class AutoRefreshProgressBarField extends ProgressBarField {
    setup() {
        super.setup();
        useEffect(() => {
            let intervalId;
            if (this.props.record.data.state === 'generating') {
                intervalId = setInterval(() => {
                    this.props.record.load();
                }, 2000);
            }
            return () => {
                if (intervalId) {
                    clearInterval(intervalId);
                }
            };
        });
    }
}

export const autoRefreshProgressBarField = {
    ...progressBarField,
    component: AutoRefreshProgressBarField,
};

registry.category("fields").add("auto_refresh_progressbar", autoRefreshProgressBarField);
