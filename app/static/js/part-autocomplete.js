/**
 * Part form autocomplete functionality
 * 
 * Handles autocomplete for manufacturer field
 * powered by data from parts table
 */
document.addEventListener('DOMContentLoaded', function() {
    // Configure autocomplete for manufacturer field
    setupAutocomplete('#manufacturer', '/parts/autocomplete/manufacturers', {
        minLength: 1,
        delay: 300
    });
});

/**
 * Setup autocomplete for a given input field
 * 
 * @param {string} selector - CSS selector for the input field
 * @param {string} url - URL to fetch autocomplete suggestions
 * @param {object} options - Additional autocomplete options
 */
function setupAutocomplete(selector, url, options) {
    const element = document.querySelector(selector);
    
    if (!element) return;

    // Default options
    const defaultOptions = {
        minLength: 2,
        delay: 300,
        source: function(request, response) {
            $.ajax({
                url: url,
                data: {
                    query: request.term
                },
                success: function(data) {
                    if (data.length === 0) {
                        // If no suggestions, still allow custom entry
                        response([{
                            label: 'Custom: ' + request.term,
                            value: request.term,
                            isCustom: true
                        }]);
                    } else {
                        response(data);
                    }
                }
            });
        },
        select: function(event, ui) {
            // If a custom value is selected, just use the raw term
            if (ui.item.isCustom) {
                $(this).val(ui.item.value.replace('Custom: ', ''));
                
                // Trigger any onSelect callback with the custom value
                if (options.onSelect) {
                    options.onSelect(ui.item.value.replace('Custom: ', ''));
                }
                
                return false;
            }
            
            // Otherwise use the suggestion and trigger any onSelect callback
            if (options.onSelect) {
                options.onSelect(ui.item.value);
            }
        }
    };

    // Merge default options with provided options
    const mergedOptions = {...defaultOptions, ...options};

    // Initialize jQuery UI autocomplete
    $(element).autocomplete(mergedOptions);

    // Add custom styling for the autocomplete menu
    $(element).autocomplete('widget').addClass('part-autocomplete-menu');
} 