// Cart functionality and interactive features

document.addEventListener('DOMContentLoaded', function() {
    // Initialize cart functionality
    initializeCart();
    
    // Initialize quantity controls
    initializeQuantityControls();
    
    // Initialize form validations
    initializeFormValidations();
});

function initializeCart() {
    // Add to cart button animations
    const addToCartButtons = document.querySelectorAll('form[action*="add_to_cart"] button[type="submit"]');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';
            this.disabled = true;
            
            // Reset button after a short delay (form will submit)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 2000);
        });
    });
}

function initializeQuantityControls() {
    // Quantity input validation
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const value = parseInt(this.value);
            const min = parseInt(this.getAttribute('min')) || 1;
            const max = parseInt(this.getAttribute('max')) || 10;
            
            if (value < min) {
                this.value = min;
                showToast('Minimum quantity is ' + min, 'warning');
            } else if (value > max) {
                this.value = max;
                showToast('Maximum quantity is ' + max, 'warning');
            }
        });
        
        // Prevent negative values on keypress
        input.addEventListener('keypress', function(e) {
            if (e.key === '-' || e.key === '+' || e.key === 'e' || e.key === 'E') {
                e.preventDefault();
            }
        });
    });
}

function initializeFormValidations() {
    // Real-time form validation
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                // Clear validation state on input
                this.classList.remove('is-invalid', 'is-valid');
            });
        });
        
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('Please check the form for errors', 'danger');
            }
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        setFieldValidation(field, false, 'This field is required');
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            setFieldValidation(field, false, 'Please enter a valid email address');
        }
    }
    
    // Password confirmation
    if (field.name === 'password2') {
        const passwordField = document.querySelector('input[name="password"]');
        if (passwordField && value !== passwordField.value) {
            isValid = false;
            setFieldValidation(field, false, 'Passwords do not match');
        }
    }
    
    // Number validation
    if (field.type === 'number' && value) {
        const num = parseFloat(value);
        const min = parseFloat(field.getAttribute('min'));
        const max = parseFloat(field.getAttribute('max'));
        
        if (!isNaN(min) && num < min) {
            isValid = false;
            setFieldValidation(field, false, `Value must be at least ${min}`);
        } else if (!isNaN(max) && num > max) {
            isValid = false;
            setFieldValidation(field, false, `Value must be at most ${max}`);
        }
    }
    
    if (isValid) {
        setFieldValidation(field, true);
    }
    
    return isValid;
}

function setFieldValidation(field, isValid, message = '') {
    field.classList.remove('is-valid', 'is-invalid');
    field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    
    // Remove existing feedback
    const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // Add feedback message for invalid fields
    if (!isValid && message) {
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        field.parentNode.appendChild(feedback);
    }
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search functionality with debounce
const searchInput = document.querySelector('input[name="search"]');
if (searchInput) {
    const debouncedSearch = debounce(function(e) {
        // Auto-submit search form after user stops typing
        if (e.target.value.length > 2 || e.target.value.length === 0) {
            e.target.form.submit();
        }
    }, 1000);
    
    searchInput.addEventListener('input', debouncedSearch);
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        // Only prevent default if it's a valid anchor link (not just '#')
        if (href && href.length > 1) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Image loading error handling
document.querySelectorAll('img').forEach(img => {
    img.addEventListener('error', function() {
        this.style.display = 'none';
        const placeholder = this.parentNode.querySelector('.img-placeholder');
        if (placeholder) {
            placeholder.style.display = 'flex';
        } else {
            // Create placeholder
            const div = document.createElement('div');
            div.className = 'bg-light rounded d-flex align-items-center justify-content-center';
            div.style.cssText = 'height: 200px; width: 100%;';
            div.innerHTML = '<i class="fas fa-image fa-2x text-muted"></i>';
            this.parentNode.insertBefore(div, this);
        }
    });
});
