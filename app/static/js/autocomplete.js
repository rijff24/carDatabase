/**
 * Autocomplete functionality for vehicle makes, models, years and colors
 * Allows users to select from existing options
 */
class VehicleAutocomplete {
    constructor(inputElement, type, options = {}) {
        this.input = inputElement;
        this.type = type; // 'make', 'model', 'year', or 'color'
        this.dropdown = null;
        this.suggestions = [];
        this.selectedIndex = -1;
        this.isDropdownVisible = false;
        this.darkMode = document.body.classList.contains('dark-mode');
        this.onSelect = options.onSelect || null; // Callback for selection

        // Create dropdown container
        this.createDropdown();
        
        // Bind events
        this.bindEvents();
        
        // Listen for dark mode changes
        this.observeDarkModeChanges();
    }

    createDropdown() {
        // Create dropdown element
        this.dropdown = document.createElement('div');
        this.dropdown.className = `autocomplete-dropdown-${this.type}`;
        this.dropdown.style.display = 'none';
        this.dropdown.style.position = 'absolute';
        this.dropdown.style.width = this.input.offsetWidth + 'px';
        this.dropdown.style.maxHeight = '200px';
        this.dropdown.style.overflowY = 'auto';
        this.applyThemeStyles();
        this.dropdown.style.borderTop = 'none';
        this.dropdown.style.borderRadius = '0 0 0.25rem 0.25rem';
        this.dropdown.style.zIndex = '1000';
        this.dropdown.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
        
        // Insert dropdown after input
        this.input.parentNode.style.position = 'relative';
        this.input.parentNode.insertBefore(this.dropdown, this.input.nextSibling);
    }
    
    applyThemeStyles() {
        // Apply styles based on current theme
        if (this.darkMode) {
            this.dropdown.style.backgroundColor = '#343a40';
            this.dropdown.style.border = '1px solid #6c757d';
            this.dropdown.style.color = '#fff';
        } else {
            this.dropdown.style.backgroundColor = '#fff';
            this.dropdown.style.border = '1px solid #ced4da';
            this.dropdown.style.color = '#212529';
        }
    }
    
    observeDarkModeChanges() {
        // Create a mutation observer to watch for dark mode changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'class' || mutation.attributeName === 'data-dark-mode') {
                    this.darkMode = document.body.classList.contains('dark-mode');
                    this.applyThemeStyles();
                    
                    // If dropdown is visible, update item styles
                    if (this.isDropdownVisible) {
                        this.updateItemStyles();
                    }
                }
            });
        });
        
        // Start observing the document body for class changes
        observer.observe(document.body, { attributes: true });
    }
    
    updateItemStyles() {
        // Update styles of existing dropdown items
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        items.forEach(item => {
            if (this.darkMode) {
                item.style.color = '#fff';
            } else {
                item.style.color = '#212529';
            }
        });
    }

    bindEvents() {
        // Input focus
        this.input.addEventListener('focus', () => {
            // Only fetch if the dropdown isn't already visible
            if (!this.isDropdownVisible) {
                this.fetchSuggestions(this.input.value.trim());
            }
        });

        // Input click - specifically handle click on empty field
        this.input.addEventListener('click', () => {
            // If dropdown isn't visible and input is empty or has minimal text, show suggestions
            if (!this.isDropdownVisible) {
                this.fetchSuggestions(this.input.value.trim());
            }
        });

        // Input keydown for Tab and Enter handling
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Tab' && this.isDropdownVisible && this.selectedIndex >= 0) {
                // Only prevent default if we're selecting from dropdown
                e.preventDefault();
                this.selectSuggestion(this.suggestions[this.selectedIndex]);
                // Manually focus the next form element
                const form = this.input.form;
                if (form) {
                    const formElements = Array.from(form.elements);
                    const currentIndex = formElements.indexOf(this.input);
                    if (currentIndex > -1 && currentIndex < formElements.length - 1) {
                        formElements[currentIndex + 1].focus();
                    }
                }
            } else if (e.key === 'Enter' && this.isDropdownVisible) {
                if (this.selectedIndex >= 0) {
                    e.preventDefault();
                    this.selectSuggestion(this.suggestions[this.selectedIndex]);
                }
            }
        });

        // Input keyup for other keys
        this.input.addEventListener('keyup', (e) => {
            // Skip for Tab and Enter (handled in keydown)
            if (e.key === 'Tab' || e.key === 'Enter') {
                return;
            }
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.selectNext();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.selectPrevious();
            } else if (e.key === 'Escape') {
                this.hideDropdown();
            } else {
                const query = this.input.value.trim();
                this.fetchSuggestions(query);
            }
        });

        // Input blur
        this.input.addEventListener('blur', (e) => {
            // Delay hiding dropdown to allow for click on suggestions
            setTimeout(() => {
                this.hideDropdown();
            }, 200);
        });

        // Document click
        document.addEventListener('click', (e) => {
            if (e.target !== this.input && e.target !== this.dropdown && !this.dropdown.contains(e.target)) {
                this.hideDropdown();
            }
        });
    }

    async fetchSuggestions(query) {
        let endpoint;
        let params = new URLSearchParams({ query: query });
        
        switch (this.type) {
            case 'make':
                endpoint = '/vehicle-data/api/makes';
                break;
            case 'model':
                endpoint = '/vehicle-data/api/models';
                // For models, we need to also check if there's a selected make
                if (document.querySelector('input[name="vehicle_make"]')) {
                    const makeValue = document.querySelector('input[name="vehicle_make"]').value.trim();
                    if (makeValue) {
                        params.append('make', makeValue);
                    }
                }
                break;
            case 'year':
                endpoint = '/vehicle-data/api/years';
                break;
            case 'color':
                endpoint = '/vehicle-data/api/colors';
                break;
            default:
                console.error(`Unknown autocomplete type: ${this.type}`);
                return;
        }
        
        try {
            const response = await fetch(`${endpoint}?${params.toString()}`);
            if (!response.ok) {
                console.error(`Error fetching ${this.type} suggestions:`, response.status);
                return;
            }
            
            const data = await response.json();
            this.suggestions = data;
            this.renderSuggestions();
            
            if (this.suggestions.length > 0) {
                this.showDropdown();
            } else {
                this.hideDropdown();
            }
        } catch (error) {
            console.error(`Error fetching ${this.type} suggestions:`, error);
            // Don't show dropdown if there was an error
            this.hideDropdown();
        }
    }

    renderSuggestions() {
        // Clear dropdown
        this.dropdown.innerHTML = '';
        this.selectedIndex = -1;

        // Add each suggestion
        this.suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.style.padding = '8px 12px';
            item.style.cursor = 'pointer';
            item.style.fontSize = '14px';
            
            // Apply theme-specific text color
            if (this.darkMode) {
                item.style.color = '#fff';
            } else {
                item.style.color = '#212529';
            }
            
            // Highlight matching part
            const query = this.input.value.trim().toLowerCase();
            if (query && suggestion.toLowerCase().includes(query)) {
                const startIdx = suggestion.toLowerCase().indexOf(query);
                const endIdx = startIdx + query.length;
                item.innerHTML = 
                    suggestion.substring(0, startIdx) + 
                    `<strong>${suggestion.substring(startIdx, endIdx)}</strong>` + 
                    suggestion.substring(endIdx);
            } else {
                item.textContent = suggestion;
            }

            // Hover effect
            item.addEventListener('mouseover', () => {
                this.selectItem(index);
            });

            // Click event
            item.addEventListener('click', () => {
                this.selectSuggestion(suggestion);
            });

            this.dropdown.appendChild(item);
        });
    }

    selectItem(index) {
        // Remove selected class from all items
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        items.forEach(item => {
            item.style.backgroundColor = '';
        });

        // Add selected class to current item
        if (index >= 0 && index < items.length) {
            if (this.darkMode) {
                items[index].style.backgroundColor = '#495057';
            } else {
                items[index].style.backgroundColor = '#f8f9fa';
            }
            this.selectedIndex = index;
        }
    }

    selectNext() {
        if (this.suggestions.length === 0) return;
        
        this.selectedIndex = (this.selectedIndex + 1) % this.suggestions.length;
        this.selectItem(this.selectedIndex);
    }

    selectPrevious() {
        if (this.suggestions.length === 0) return;
        
        this.selectedIndex = (this.selectedIndex - 1 + this.suggestions.length) % this.suggestions.length;
        this.selectItem(this.selectedIndex);
    }

    selectSuggestion(suggestion) {
        // Set the input value
        this.input.value = suggestion;
        this.hideDropdown();
        
        // Call onSelect callback if defined
        if (typeof this.onSelect === 'function') {
            this.onSelect(suggestion, this.type);
        }
        
        // Dispatch a change event to trigger any event listeners
        const event = new Event('change', { bubbles: true });
        this.input.dispatchEvent(event);
        
        // Also dispatch an input event for completeness
        const inputEvent = new Event('input', { bubbles: true });
        this.input.dispatchEvent(inputEvent);
        
        // Focus the input to ensure the value is registered
        this.input.focus();
    }

    showDropdown() {
        // Position dropdown directly below input
        this.dropdown.style.width = this.input.offsetWidth + 'px';
        this.dropdown.style.display = 'block';
        this.isDropdownVisible = true;
    }

    hideDropdown() {
        this.dropdown.style.display = 'none';
        this.isDropdownVisible = false;
    }
}

// Initialize autocomplete for makes, models, years and colors
document.addEventListener('DOMContentLoaded', function() {
    // Function to set up make-model relationship
    function setupMakeModelRelationship() {
        const makeField = document.querySelector('input[name="vehicle_make"]');
        const modelField = document.querySelector('input[name="vehicle_model"]');
        
        if (makeField && modelField) {
            // Store original values for reference
            const originalMake = makeField.value.trim();
            const originalModel = modelField.value.trim();
            
            // Handle make changes to filter models
            makeField.addEventListener('change', function() {
                const newMake = this.value.trim();
                // Only clear model if make has changed from its original value
                if (newMake !== originalMake) {
                    modelField.value = '';
                }
            });
        }
    }
    
    // Handle model field enabling/disabling on create page
    function setupCreatePageBehavior() {
        const makeInput = document.getElementById('vehicle_make');
        const modelInput = document.getElementById('vehicle_model');
        
        // Only proceed if we're on the create page (identified by disabled model field)
        if (makeInput && modelInput && modelInput.disabled) {
            // Function to enable model field
            function enableModelField() {
                modelInput.disabled = false;
                modelInput.classList.remove('bg-light', 'text-muted');
                modelInput.style.cursor = 'text';
                modelInput.placeholder = '';
            }
            
            // Function to disable model field
            function disableModelField() {
                modelInput.disabled = true;
                modelInput.classList.add('bg-light', 'text-muted');
                modelInput.style.cursor = 'not-allowed';
                modelInput.placeholder = 'Select make first';
                modelInput.value = '';
            }
            
            // Enable/disable model field based on make value
            makeInput.addEventListener('input', function() {
                if (this.value.trim()) {
                    enableModelField();
                } else {
                    disableModelField();
                }
            });
            
            // Also trigger on change event
            makeInput.addEventListener('change', function() {
                if (this.value.trim()) {
                    enableModelField();
                } else {
                    disableModelField();
                }
            });
        }
    }

    // Initialize makes
    const makeInputs = document.querySelectorAll('input[name="vehicle_make"]');
    makeInputs.forEach(input => {
        new VehicleAutocomplete(input, 'make');
    });
    
    // Initialize models
    const modelInputs = document.querySelectorAll('input[name="vehicle_model"]');
    modelInputs.forEach(input => {
        new VehicleAutocomplete(input, 'model');
    });
    
    // Initialize years
    const yearInputs = document.querySelectorAll('input[name="year"]');
    yearInputs.forEach(input => {
        new VehicleAutocomplete(input, 'year');
    });
    
    // Initialize colors
    const colorInputs = document.querySelectorAll('input[name="colour"]');
    colorInputs.forEach(input => {
        new VehicleAutocomplete(input, 'color');
    });
    
    // Set up make-model relationship after autocomplete is initialized
    setupMakeModelRelationship();
    
    // Set up create page specific behavior
    setupCreatePageBehavior();
}); 