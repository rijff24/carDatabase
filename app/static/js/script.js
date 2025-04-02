// Enable Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add confirmation for delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Form validation styles
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Date picker initialization
    const datePickers = document.querySelectorAll('.datepicker');
    if (datePickers.length) {
        datePickers.forEach(el => {
            el.addEventListener('focus', function() {
                this.type = 'date';
            });
            el.addEventListener('blur', function() {
                if (!this.value) {
                    this.type = 'text';
                }
            });
        });
    }
    
    // Filter dropdown change handlers
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            this.form.submit();
        });
    });
    
    // Table row click to navigate
    const dataRows = document.querySelectorAll('tr[data-href]');
    dataRows.forEach(row => {
        row.addEventListener('click', function() {
            window.location.href = this.dataset.href;
        });
        row.style.cursor = 'pointer';
    });
    
    // Dark mode initialization
    initDarkMode();
});

// Function to initialize dark mode based on setting
function initDarkMode() {
    // Check for dark mode flag in HTML (set by backend)
    const darkModeEnabled = document.body.dataset.darkMode === 'true';
    
    if (darkModeEnabled) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
    
    // Add event listener for dark mode toggle checkbox
    const darkModeToggle = document.getElementById('enable_dark_mode');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                enableDarkMode();
                // Need to submit the form to save the setting, but don't want to reload the page yet
                const form = this.closest('form');
                const formData = new FormData(form);
                
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (response.ok) {
                        console.log('Dark mode setting saved');
                    }
                })
                .catch(error => {
                    console.error('Error saving dark mode setting:', error);
                });
                
                return false;
            } else {
                disableDarkMode();
                // Same as above for saving the setting
                const form = this.closest('form');
                const formData = new FormData(form);
                
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (response.ok) {
                        console.log('Dark mode setting saved');
                    }
                })
                .catch(error => {
                    console.error('Error saving dark mode setting:', error);
                });
                
                return false;
            }
        });
    }
}

// Function to enable dark mode
function enableDarkMode() {
    document.body.classList.add('dark-mode');
    document.body.dataset.darkMode = 'true';
    localStorage.setItem('darkMode', 'enabled');
}

// Function to disable dark mode
function disableDarkMode() {
    document.body.classList.remove('dark-mode');
    document.body.dataset.darkMode = 'false';
    localStorage.setItem('darkMode', 'disabled');
} 