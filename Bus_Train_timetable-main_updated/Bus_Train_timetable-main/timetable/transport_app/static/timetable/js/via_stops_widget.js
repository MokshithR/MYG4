// timetable/static/timetable/js/via_stops_widget.js

(function($) {
    $(document).ready(function() {
        // Function to initialize the dynamic formset for a given field name
        function initializeViaStopsWidget(fieldIdPrefix) {
            const container = $(`#${fieldIdPrefix}_container`);
            const addButton = $(`#${fieldIdPrefix}_add_item`);
            const template = container.find('.via-stops-template').html(); // Get the template for a new row

            let nextIndex = container.find('.via-stops-item').length; // Start index for new items

            // Function to update input names/ids based on index
            function updateElementIndexes(element, index) {
                element.find('[name]').each(function() {
                    const name = $(this).attr('name');
                    // Replace '___index___' placeholder with the actual index
                    $(this).attr('name', name.replace('___index___', index));
                });
                element.find('[id]').each(function() {
                    const id = $(this).attr('id');
                    // Replace '___index___' placeholder with the actual index
                    $(this).attr('id', id.replace('___index___', index));
                });
            }

            // Add new item
            addButton.on('click', function() {
                const newRow = $(template.replace(/___index___/g, nextIndex));
                container.append(newRow);
                nextIndex++;
                newRow.find('.remove-item-button').on('click', function() {
                    $(this).closest('.via-stops-item').remove();
                    // No need to re-index, we'll parse the JSON on save
                });
            });

            // Initial setup for existing items and remove button click handler
            container.find('.via-stops-item').each(function() {
                $(this).find('.remove-item-button').on('click', function() {
                    $(this).closest('.via-stops-item').remove();
                });
            });

            // Handle initial JSON data from the textarea
            const jsonTextarea = $(`#${fieldIdPrefix}_json`);
            if (jsonTextarea.length && jsonTextarea.val()) {
                try {
                    const data = JSON.parse(jsonTextarea.val());
                    if (Array.isArray(data)) {
                        container.empty(); // Clear template container
                        nextIndex = 0; // Reset index for parsing existing data
                        data.forEach(function(item) {
                            const newRow = $(template.replace(/___index___/g, nextIndex));
                            // Fill in existing values
                            newRow.find(`[name$="___index___.stop"]`).val(item.stop || '');
                            newRow.find(`[name$="___index___.time"]`).val(item.time || '');
                            updateElementIndexes(newRow, nextIndex); // Update names/ids for existing rows
                            container.append(newRow);
                            nextIndex++;
                        });
                        // Attach remove listeners to newly added existing rows
                        container.find('.via-stops-item').each(function() {
                            $(this).find('.remove-item-button').on('click', function() {
                                $(this).closest('.via-stops-item').remove();
                            });
                        });
                    }
                } catch (e) {
                    console.error("Error parsing JSON for via_stops:", e);
                    // Leave the textarea as is if JSON is invalid
                }
            }

            // Intercept form submission to consolidate data into JSONField
            $('form#busroute_form, form#trainroute_form').on('submit', function() { // Adjust form IDs as per your admin's form
                const items = [];
                container.find('.via-stops-item').each(function() {
                    const stop = $(this).find('input[name$=".stop"]').val();
                    const time = $(this).find('input[name$=".time"]').val();
                    if (stop || time) { // Only add if at least one field has content
                        items.push({ stop: stop, time: time });
                    }
                });
                jsonTextarea.val(JSON.stringify(items)); // Update the hidden JSONField
            });
        }

        // Initialize for BusRoute and TrainRoute via_stops fields
        initializeViaStopsWidget('id_via_stops'); // This is the default ID for a field named 'via_stops'

        // Django admin's dynamically added inlines need re-initialization
        // This watches for new inline rows to be added (e.g., if BusRoute is an inline itself)
        $(document).on('formset:added', function(event, row) {
            // Find if the added row contains a via_stops field
            const viaStopsField = row.find('[id$="_via_stops_json"]');
            if (viaStopsField.length) {
                const fieldIdPrefix = viaStopsField.attr('id').replace('_json', '');
                initializeViaStopsWidget(fieldIdPrefix);
            }
        });

    });
})(django.jQuery); // Use django.jQuery to avoid conflicts