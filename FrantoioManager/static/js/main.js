// Main JavaScript file for the olive oil mill management system

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete operations
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-delete') || 
                          'Sei sicuro di voler eliminare questo elemento?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Form validation helpers
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-format phone numbers
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            // Simple phone number formatting (Italian style)
            let value = this.value.replace(/\D/g, '');
            if (value.length > 3 && value.length <= 6) {
                value = value.replace(/(\d{3})(\d+)/, '$1 $2');
            } else if (value.length > 6) {
                value = value.replace(/(\d{3})(\d{3})(\d+)/, '$1 $2 $3');
            }
            this.value = value;
        });
    });

    // Auto-uppercase text inputs for names
    const nameInputs = document.querySelectorAll('input[name="nome"], input[name="cognome"]');
    nameInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/\b\w/g, function(l) {
                return l.toUpperCase();
            });
        });
    });

    // Prevent double form submission
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form) {
                setTimeout(() => {
                    this.disabled = true;
                    this.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Attendere...';
                }, 100);
            }
        });
    });
});

// Utility functions

/**
 * Format date to Italian format
 */
function formatDateIT(date) {
    return new Date(date).toLocaleDateString('it-IT');
}

/**
 * Format datetime to Italian format
 */
function formatDateTimeIT(datetime) {
    return new Date(datetime).toLocaleString('it-IT');
}

/**
 * Validate email format
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate Italian phone number
 */
function validatePhoneIT(phone) {
    const re = /^(\+39)?[\s]?[0-9]{3}[\s]?[0-9]{3}[\s]?[0-9]{3,4}$/;
    return re.test(phone.replace(/\s/g, ''));
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

/**
 * Confirm action with custom message
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        if (typeof callback === 'function') {
            callback();
        }
        return true;
    }
    return false;
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

/**
 * Format number as currency (Euro)
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('it-IT', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

/**
 * Scroll to top
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll to top functionality
window.addEventListener('scroll', function() {
    const scrollButton = document.getElementById('scroll-top');
    if (scrollButton) {
        if (window.pageYOffset > 300) {
            scrollButton.style.display = 'block';
        } else {
            scrollButton.style.display = 'none';
        }
    }
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    showNotification('Si è verificato un errore. Ricarica la pagina e riprova.', 'danger');
});

// Handle offline/online status
window.addEventListener('online', function() {
    showNotification('Connessione ripristinata', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Modalità offline attiva', 'warning');
});

// Export utility functions for use in other scripts
window.FrantOlioUtils = {
    formatDateIT,
    formatDateTimeIT,
    validateEmail,
    validatePhoneIT,
    showNotification,
    confirmAction,
    debounce,
    formatCurrency,
    scrollToTop
};
