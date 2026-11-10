/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class TimetableMatrixField extends Component {
    setup() {
        this.action = useService("action");
    }
    
    get markupValue() {
        return this.props.record.data[this.props.name] || "";
    }

    onClick(ev) {
        const cell = ev.target.closest('.force-assign-cell');
        if (cell) {
            ev.preventDefault();
            ev.stopPropagation();
            
            const dataset = cell.dataset;
            this.action.doAction('timetable_creator.action_open_force_assign_wizard', {
                additionalContext: {
                    default_table_id: parseInt(dataset.tableId),
                    default_day: dataset.day,
                    default_start_time: parseFloat(dataset.startTime),
                    default_end_time: parseFloat(dataset.endTime),
                }
            });
        }
    }
}

TimetableMatrixField.template = xml`
    <div class="o_timetable_matrix" t-on-click="onClick">
        <t t-out="markupValue"/>
    </div>
`;

TimetableMatrixField.props = {
    ...standardFieldProps,
};

registry.category("fields").add("timetable_matrix", {
    component: TimetableMatrixField,
});
