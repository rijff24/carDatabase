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
    
    // Initialize mobile features
    initMobileFeatures();
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

// ===== MOBILE FEATURES INITIALIZATION =====
function initMobileFeatures() {
    // Mobile device detection
    const isMobile = detectMobileDevice();
    const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    if (isMobile) {
        document.body.classList.add('mobile-device');
    }
    
    if (isTouch) {
        document.body.classList.add('touch-device');
    }
    
    // Initialize mobile navigation
    initMobileNavigation();
    
    // Initialize mobile tables
    initMobileTables();
    
    // Initialize touch gestures
    if (isTouch) {
        initTouchGestures();
    }
    
    // Initialize mobile forms
    initMobileForms();
    
    // Initialize mobile utilities
    initMobileUtilities();
}



// Mobile device detection
function detectMobileDevice() {
    return window.innerWidth <= 991 || 
           /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Mobile navigation enhancements
function initMobileNavigation() {
    const navbar = document.querySelector('.navbar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (!navbar || !navbarToggler || !navbarCollapse) return;
    
    // Enhanced hamburger menu behavior
    navbarToggler.addEventListener('click', function() {
        const isExpanded = navbarToggler.getAttribute('aria-expanded') === 'true';
        
        // Add mobile-specific classes
        if (!isExpanded) {
            document.body.classList.add('mobile-nav-open');
        } else {
            document.body.classList.remove('mobile-nav-open');
        }
    });
    
    // Close navigation when clicking outside
    document.addEventListener('click', function(e) {
        if (!navbar.contains(e.target) && navbarCollapse.classList.contains('show')) {
            navbarToggler.click();
        }
    });
    
    // Close navigation when clicking on nav links (mobile)
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 991 && navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });
    });
    
    // Mobile dropdown enhancements
    const dropdownToggle = document.querySelectorAll('.navbar-nav .dropdown-toggle');
    dropdownToggle.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth <= 991) {
                e.preventDefault();
                const dropdown = this.nextElementSibling;
                if (dropdown && dropdown.classList.contains('dropdown-menu')) {
                    dropdown.classList.toggle('show');
                }
            }
        });
    });
}

// Mobile tables initialization
function initMobileTables() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        // Add mobile stack class for small screens
        if (window.innerWidth <= 575) {
            table.classList.add('table-mobile-stack');
            
            // Add data labels for mobile view
            const headerCells = table.querySelectorAll('thead th');
            const bodyRows = table.querySelectorAll('tbody tr');
            
            bodyRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                cells.forEach((cell, index) => {
                    if (headerCells[index]) {
                        cell.setAttribute('data-label', headerCells[index].textContent.trim());
                    }
                });
            });
        }
    });
    
    // Handle table scrolling on mobile
    const tableResponsive = document.querySelectorAll('.table-responsive');
    tableResponsive.forEach(container => {
        let isScrolling = false;
        
        container.addEventListener('touchstart', () => {
            isScrolling = false;
        });
        
        container.addEventListener('touchmove', () => {
            isScrolling = true;
        });
        
        container.addEventListener('touchend', () => {
            if (!isScrolling) {
                // Handle tap on table row
                const target = event.target.closest('tr[data-href]');
                if (target && target.dataset.href) {
                    window.location.href = target.dataset.href;
                }
            }
        });
    });
}

// Touch gestures initialization
function initTouchGestures() {
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;
    
    // Swipe gestures for navigation
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });
    
    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipeGesture();
    }, { passive: true });
    
    function handleSwipeGesture() {
        const swipeThreshold = 100;
        const swipeVelocity = 0.3;
        
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;
        
        // Check if it's a horizontal swipe
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            // Right swipe - could open navigation
            if (deltaX > swipeThreshold) {
                const navbarToggler = document.querySelector('.navbar-toggler');
                const navbarCollapse = document.querySelector('.navbar-collapse');
                
                if (navbarToggler && navbarCollapse && !navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            }
            // Left swipe - could close navigation
            else if (deltaX < -swipeThreshold) {
                const navbarToggler = document.querySelector('.navbar-toggler');
                const navbarCollapse = document.querySelector('.navbar-collapse');
                
                if (navbarToggler && navbarCollapse && navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            }
        }
    }
    
    // Pull to refresh (for future implementation)
    let pullToRefreshThreshold = 60;
    let pullDistance = 0;
    
    // Add haptic feedback for supported devices
    function hapticFeedback() {
        if (navigator.vibrate) {
            navigator.vibrate(10);
        }
    }
    
    // Touch feedback for buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        }, { passive: true });
        
        button.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        }, { passive: true });
    });
}

// Mobile forms enhancement
function initMobileForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Add mobile form class if on mobile
        if (window.innerWidth <= 575) {
            form.classList.add('mobile-form-stack');
        }
        
        // Enhanced mobile input focus
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                // Scroll to input on mobile to ensure visibility
                if (window.innerWidth <= 575) {
                    setTimeout(() => {
                        this.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'center' 
                        });
                    }, 300);
                }
            });
        });
    });
    
    // Mobile-friendly date pickers
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Ensure consistent appearance across mobile browsers
        input.style.minHeight = '44px';
    });
}

// Mobile utility functions
function initMobileUtilities() {
    // Viewport height fix for mobile browsers
    function setViewportHeight() {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    
    setViewportHeight();
    window.addEventListener('resize', setViewportHeight);
    window.addEventListener('orientationchange', setViewportHeight);
    
    // Mobile keyboard handling
    const viewport = document.querySelector('meta[name=viewport]');
    if (viewport) {
        window.addEventListener('focusin', function() {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1, maximum-scale=1');
        });
        
        window.addEventListener('focusout', function() {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1');
        });
    }
    
    // Mobile card animations
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('touchstart', function() {
            if (!this.classList.contains('no-touch-animation')) {
                this.style.transform = 'scale(0.98)';
                this.style.transition = 'transform 0.1s ease';
            }
        }, { passive: true });
        
        card.addEventListener('touchend', function() {
            if (!this.classList.contains('no-touch-animation')) {
                this.style.transform = 'scale(1)';
            }
        }, { passive: true });
    });
    
    // Mobile table row highlighting
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('touchstart', function() {
            this.style.backgroundColor = 'rgba(13, 110, 253, 0.1)';
        }, { passive: true });
        
        row.addEventListener('touchend', function() {
            setTimeout(() => {
                this.style.backgroundColor = '';
            }, 150);
        }, { passive: true });
    });
}

// Mobile orientation change handler
window.addEventListener('orientationchange', function() {
    // Force repaint to fix layout issues
    document.body.style.display = 'none';
    document.body.offsetHeight; // Trigger reflow
    document.body.style.display = '';
    
    // Re-initialize mobile tables if needed
    setTimeout(() => {
        initMobileTables();
    }, 100);
});

// Export mobile utilities for external use
window.mobileUtils = {
    isMobile: detectMobileDevice,
    isTouch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
    initMobileFeatures: initMobileFeatures,
    addTouchFeedback: function(element) {
        element.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        }, { passive: true });
        
        element.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        }, { passive: true });
    }
}; 