// Academic Timetable Generator - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeTimetable();
    initializeModals();
    initializeTooltips();
    initializeFormValidation();
});

// Initialize timetable-specific functionality
function initializeTimetable() {
    // Add click handlers for schedule entries
    const scheduleEntries = document.querySelectorAll('.schedule-entry');
    scheduleEntries.forEach(entry => {
        entry.addEventListener('click', function() {
            const entryId = this.dataset.entryId;
            if (entryId) {
                showEntryDetails(entryId);
            }
        });
    });

    // Initialize drag and drop if edit permissions available
    if (hasEditPermissions()) {
        initializeDragAndDrop();
    }
}

// Initialize Bootstrap modals
function initializeModals() {
    // Auto-focus first input in modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });

    // Prevent modal backdrop clicks from closing critical modals
    const criticalModals = document.querySelectorAll('[data-critical="true"]');
    criticalModals.forEach(modal => {
        modal.setAttribute('data-bs-backdrop', 'static');
        modal.setAttribute('data-bs-keyboard', 'false');
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showValidationErrors(form);
            }
            form.classList.add('was-validated');
        });
    });

    // Real-time validation for specific fields
    initializeFieldValidation();
}

// Initialize field-specific validation
function initializeFieldValidation() {
    // Email validation
    const emailFields = document.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateEmail(this);
        });
    });

    // Time validation
    const timeFields = document.querySelectorAll('input[type="time"]');
    timeFields.forEach(field => {
        field.addEventListener('change', function() {
            validateTimeRange(this);
        });
    });

    // Course code validation
    const codeFields = document.querySelectorAll('input[name*="code"]');
    codeFields.forEach(field => {
        field.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
            validateCourseCode(this);
        });
    });
}

// Validation functions
function validateEmail(field) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = emailRegex.test(field.value);
    
    setFieldValidation(field, isValid, 'Please enter a valid email address');
    return isValid;
}

function validateTimeRange(field) {
    const form = field.closest('form');
    const startTimeField = form.querySelector('input[name="start_time"]');
    const endTimeField = form.querySelector('input[name="end_time"]');
    
    if (startTimeField && endTimeField && startTimeField.value && endTimeField.value) {
        const startTime = new Date(`1970-01-01T${startTimeField.value}`);
        const endTime = new Date(`1970-01-01T${endTimeField.value}`);
        const isValid = startTime < endTime;
        
        setFieldValidation(endTimeField, isValid, 'End time must be after start time');
        return isValid;
    }
    return true;
}

function validateCourseCode(field) {
    const codeRegex = /^[A-Z0-9\-\s]{2,20}$/;
    const isValid = codeRegex.test(field.value);
    
    setFieldValidation(field, isValid, 'Course code must be 2-20 characters (letters, numbers, hyphens, spaces only)');
    return isValid;
}

function setFieldValidation(field, isValid, errorMessage) {
    field.classList.toggle('is-valid', isValid);
    field.classList.toggle('is-invalid', !isValid);
    
    let feedback = field.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentNode.appendChild(feedback);
    }
    feedback.textContent = isValid ? '' : errorMessage;
}

// Show validation errors
function showValidationErrors(form) {
    const invalidFields = form.querySelectorAll(':invalid');
    if (invalidFields.length > 0) {
        invalidFields[0].focus();
        showAlert('Please correct the highlighted errors', 'error');
    }
}

// Entry details modal
function showEntryDetails(entryId) {
    // This would typically make an AJAX call to get entry details
    console.log('Showing details for entry:', entryId);
    // Implementation would depend on specific requirements
}

// Check if user has edit permissions
function hasEditPermissions() {
    const userRole = document.body.dataset.userRole;
    return userRole === 'admin' || userRole === 'faculty';
}

// Initialize drag and drop for timetable editing
function initializeDragAndDrop() {
    const scheduleEntries = document.querySelectorAll('.schedule-entry');
    
    scheduleEntries.forEach(entry => {
        entry.draggable = true;
        entry.addEventListener('dragstart', handleDragStart);
        entry.addEventListener('dragover', handleDragOver);
        entry.addEventListener('drop', handleDrop);
        entry.addEventListener('dragend', handleDragEnd);
    });
}

// Drag and drop handlers
function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', this.dataset.entryId);
    this.classList.add('dragging');
}

function handleDragOver(e) {
    e.preventDefault();
    this.classList.add('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    const entryId = e.dataTransfer.getData('text/plain');
    const targetCell = this.closest('td');
    
    if (targetCell && entryId) {
        // This would make an AJAX call to update the entry
        console.log('Moving entry', entryId, 'to new cell');
        // Implementation would depend on backend API
    }
    
    this.classList.remove('drag-over');
}

function handleDragEnd() {
    this.classList.remove('dragging');
    document.querySelectorAll('.drag-over').forEach(el => {
        el.classList.remove('drag-over');
    });
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertContainer, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(alertContainer);
        alert.close();
    }, 5000);
}

function showLoading(element) {
    element.classList.add('loading');
    element.style.position = 'relative';
}

function hideLoading(element) {
    element.classList.remove('loading');
}

// Export functions
function exportTimetable(format) {
    showLoading(document.querySelector('.btn-group'));
    
    const url = `/export/${format}`;
    window.location.href = url;
    
    setTimeout(() => {
        hideLoading(document.querySelector('.btn-group'));
    }, 2000);
}

// Auto-save functionality for forms
function initializeAutoSave() {
    const forms = document.querySelectorAll('[data-autosave="true"]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                saveFormData(form);
            });
        });
    });
}

function saveFormData(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    localStorage.setItem(`form_${form.id}`, JSON.stringify(data));
    showAlert('Changes saved automatically', 'success');
}

function restoreFormData(form) {
    const savedData = localStorage.getItem(`form_${form.id}`);
    
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = data[key];
            }
        });
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save forms
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            activeForm.requestSubmit();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Print functionality
function printTimetable() {
    const printWindow = window.open('', '_blank');
    const timetableContent = document.querySelector('.table-responsive').innerHTML;
    
    printWindow.document.write(`
        <html>
        <head>
            <title>Timetable - Academic Timetable Generator</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                @media print {
                    .btn, .no-print { display: none !important; }
                    .table { font-size: 0.8rem; }
                    .schedule-entry { background: #f8f9fa !important; color: #000 !important; }
                }
            </style>
        </head>
        <body>
            <div class="container-fluid">
                <h2>Academic Timetable</h2>
                <div class="table-responsive">${timetableContent}</div>
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
}

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('#timetableSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            filterTimetableEntries(searchTerm);
        });
    }
}

function filterTimetableEntries(searchTerm) {
    const entries = document.querySelectorAll('.schedule-entry');
    
    entries.forEach(entry => {
        const text = entry.textContent.toLowerCase();
        const shouldShow = text.includes(searchTerm);
        
        entry.style.display = shouldShow ? 'block' : 'none';
        
        // Highlight matching text
        if (searchTerm && shouldShow) {
            highlightText(entry, searchTerm);
        }
    });
}

function highlightText(element, searchTerm) {
    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    const textNodes = [];
    let node;
    
    while (node = walker.nextNode()) {
        textNodes.push(node);
    }
    
    textNodes.forEach(textNode => {
        const parent = textNode.parentNode;
        const text = textNode.textContent;
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        
        if (regex.test(text)) {
            const highlightedText = text.replace(regex, '<mark>$1</mark>');
            const wrapper = document.createElement('span');
            wrapper.innerHTML = highlightedText;
            parent.replaceChild(wrapper, textNode);
        }
    });
}

// Initialize all functionality when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeAutoSave();
    initializeSearch();
    
    // Restore form data on page load
    const forms = document.querySelectorAll('[data-autosave="true"]');
    forms.forEach(restoreFormData);
});
