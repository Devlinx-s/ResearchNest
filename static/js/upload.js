// ResearchNest Upload Form JavaScript
// Handles file uploads, drag & drop, and form validation

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    const uploadArea = document.getElementById('uploadArea');
    const uploadPrompt = document.getElementById('uploadPrompt');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFileBtn = document.getElementById('removeFile');
    const submitBtn = document.getElementById('submitBtn');
    const uploadForm = document.getElementById('uploadForm');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = progressContainer ? progressContainer.querySelector('.progress-bar') : null;
    const extractionStatus = document.getElementById('extractionStatus');
    const extractionMessage = document.getElementById('extractionMessage');

    // File size limit (20MB)
    const MAX_FILE_SIZE = 20 * 1024 * 1024;

    // Initialize drag and drop
    initializeDragAndDrop();
    
    // Initialize file input change handler
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // Initialize remove file button
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', clearFile);
    }
    
    // Initialize form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFormSubmit);
    }

    function initializeDragAndDrop() {
        if (!uploadArea) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        uploadArea.addEventListener('drop', handleDrop, false);
        
        // Handle click to open file dialog
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        uploadArea.classList.add('dragover');
    }

    function unhighlight(e) {
        uploadArea.classList.remove('dragover');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    }

    function handleFile(file) {
        // Validate file type
        if (!file.type === 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
            showAlert('Please select a PDF file only.', 'error');
            clearFile();
            return;
        }

        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            showAlert(`File size exceeds 20MB limit. Your file is ${formatFileSize(file.size)}.`, 'error');
            clearFile();
            return;
        }

        // Update UI to show selected file
        displaySelectedFile(file);
        
        // Show extraction status
        showExtractionStatus('File selected. Metadata will be extracted during upload.', 'info');
    }

    function displaySelectedFile(file) {
        if (uploadPrompt) uploadPrompt.style.display = 'none';
        if (fileInfo) fileInfo.style.display = 'block';
        if (fileName) fileName.textContent = `${file.name} (${formatFileSize(file.size)})`;
        
        // Enable submit button
        if (submitBtn) submitBtn.disabled = false;
    }

    function clearFile() {
        if (fileInput) fileInput.value = '';
        if (uploadPrompt) uploadPrompt.style.display = 'block';
        if (fileInfo) fileInfo.style.display = 'none';
        if (extractionStatus) extractionStatus.style.display = 'none';
        
        // Disable submit button
        if (submitBtn) submitBtn.disabled = true;
        
        // Clear any validation states
        clearValidationStates();
    }

    function handleFormSubmit(e) {
        // Basic client-side validation
        if (!fileInput.files[0]) {
            e.preventDefault();
            showAlert('Please select a PDF file to upload.', 'error');
            return;
        }

        // Show progress
        showProgress();
        
        // Show processing message
        showExtractionStatus('Uploading file and extracting metadata...', 'info');
        
        // Disable submit button to prevent double submission
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i data-feather="loader" class="me-1"></i>Processing...';
            feather.replace();
        }
    }

    function showProgress() {
        if (progressContainer) {
            progressContainer.style.display = 'block';
            if (progressBar) {
                progressBar.style.width = '0%';
                // Simulate progress
                let progress = 0;
                const interval = setInterval(() => {
                    progress += Math.random() * 15;
                    if (progress > 90) progress = 90;
                    progressBar.style.width = progress + '%';
                    if (progress >= 90) clearInterval(interval);
                }, 200);
            }
        }
    }

    function showExtractionStatus(message, type) {
        if (extractionStatus && extractionMessage) {
            extractionMessage.textContent = message;
            extractionStatus.className = `alert alert-${type === 'error' ? 'danger' : type}`;
            extractionStatus.style.display = 'block';
        }
    }

    function clearValidationStates() {
        // Clear any Bootstrap validation classes
        const inputs = uploadForm.querySelectorAll('.form-control, .form-select');
        inputs.forEach(input => {
            input.classList.remove('is-valid', 'is-invalid');
        });
        
        // Clear error messages
        const errorMessages = uploadForm.querySelectorAll('.invalid-feedback');
        errorMessages.forEach(msg => {
            msg.style.display = 'none';
        });
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of container
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }

    // Real-time form validation
    function initializeRealTimeValidation() {
        const titleInput = document.getElementById('title');
        const authorsInput = document.getElementById('authors');
        const yearInput = document.getElementById('publication_year');
        const departmentSelect = document.getElementById('department_id');

        // Title validation
        if (titleInput) {
            titleInput.addEventListener('input', function() {
                validateTextField(this, 1, 255, 'Title must be between 1 and 255 characters.');
            });
        }

        // Authors validation
        if (authorsInput) {
            authorsInput.addEventListener('input', function() {
                validateTextField(this, 1, 500, 'Authors field must be between 1 and 500 characters.');
            });
        }

        // Year validation
        if (yearInput) {
            yearInput.addEventListener('input', function() {
                validateYear(this);
            });
        }

        // Department validation
        if (departmentSelect) {
            departmentSelect.addEventListener('change', function() {
                validateSelect(this, 'Please select a department.');
            });
        }
    }

    function validateTextField(input, minLength, maxLength, message) {
        const value = input.value.trim();
        const isValid = value.length >= minLength && value.length <= maxLength;
        
        updateValidationState(input, isValid, message);
        return isValid;
    }

    function validateYear(input) {
        const value = parseInt(input.value);
        const currentYear = new Date().getFullYear();
        const isValid = !isNaN(value) && value >= 1900 && value <= currentYear + 1;
        
        updateValidationState(input, isValid, `Year must be between 1900 and ${currentYear + 1}.`);
        return isValid;
    }

    function validateSelect(select, message) {
        const isValid = select.value && select.value !== '0';
        updateValidationState(select, isValid, message);
        return isValid;
    }

    function updateValidationState(input, isValid, message) {
        const feedback = input.parentNode.querySelector('.invalid-feedback');
        
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            if (feedback) feedback.style.display = 'none';
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            if (feedback) {
                feedback.textContent = message;
                feedback.style.display = 'block';
            }
        }
    }

    // Initialize real-time validation
    initializeRealTimeValidation();

    // Character counters for text fields
    function initializeCharacterCounters() {
        const textInputs = document.querySelectorAll('input[type="text"], textarea');
        
        textInputs.forEach(input => {
            const maxLength = input.getAttribute('maxlength');
            if (maxLength) {
                createCharacterCounter(input, parseInt(maxLength));
            }
        });
    }

    function createCharacterCounter(input, maxLength) {
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        counter.style.fontSize = '0.875rem';
        
        function updateCounter() {
            const currentLength = input.value.length;
            counter.textContent = `${currentLength}/${maxLength}`;
            
            if (currentLength > maxLength * 0.9) {
                counter.className = 'form-text text-end text-warning';
            } else if (currentLength === maxLength) {
                counter.className = 'form-text text-end text-danger';
            } else {
                counter.className = 'form-text text-end text-muted';
            }
        }
        
        input.addEventListener('input', updateCounter);
        input.parentNode.appendChild(counter);
        updateCounter();
    }

    // Initialize character counters
    initializeCharacterCounters();
});
