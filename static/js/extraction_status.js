/**
 * @file extraction_status.js
 * @description Handles real-time updates for document processing status with WebSocket and fallback to polling.
 * This module provides a user interface that shows the progress of document processing,
 * including page analysis, question extraction, and saving results. It uses WebSockets
 * for real-time updates with a fallback to AJAX polling if WebSockets are unavailable.
 * 
 * Features:
 * - Real-time progress updates via WebSocket
 * - Fallback to AJAX polling if WebSockets fail
 * - Visual progress indicators and status cards
 * - Error handling with user feedback
 * - Responsive design for different screen sizes
 * 
 * @requires Socket.IO client library
 * @requires Feather Icons
 * @requires Bootstrap 5
 */

/**
 * @namespace ExtractionStatus
 * @description Main namespace for the extraction status functionality
 */

/**
 * @typedef {Object} StatusElement
 * @property {HTMLElement} element - The container element for the status
 * @property {HTMLElement} icon - The icon element
 * @property {HTMLElement} text - The text element
 * @property {HTMLElement} [time] - The time element (optional)
 * @property {Object} [progress] - Progress bar elements (optional)
 */

/**
 * @typedef {Object} ExtractionStatusData
 * @property {string} status - Current status ('pending'|'processing'|'extracting'|'saving'|'completed'|'failed')
 * @property {number} [progress] - Overall progress percentage
 * @property {Object} [page_analysis] - Page analysis progress
 * @property {number} [page_analysis.current_page] - Current page being processed
 * @property {number} [page_analysis.total_pages] - Total pages to process
 * @property {number} [questions_extracted] - Number of questions extracted
 * @property {string} [message] - Status or error message
 * @property {string} [failed_step] - Which step failed (if any)
 * @property {string} [timestamp] - When the status was last updated
 */

// Wait for the DOM to be fully loaded before initializing the extraction status
document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    /**
     * @type {Object} DOM Elements used throughout the application
     * @property {HTMLElement} statusText - Displays the current status message
     * @property {HTMLElement} progressBar - Main progress bar element
     * @property {HTMLElement} progressPercent - Displays the progress percentage
     * @property {HTMLElement} elapsedTime - Shows how long the extraction has been running
     * @property {HTMLElement} lastUpdated - Shows when the status was last updated
     * @property {HTMLElement} completionCard - Shown when extraction is complete
     * @property {HTMLElement} errorCard - Shown when an error occurs
     * @property {HTMLElement} errorMessage - Displays error details
     * @property {HTMLElement} retryBtn - Button to retry failed extraction
     * @property {HTMLElement} viewQuestionsBtn - Button to view extracted questions
     */
    // DOM Elements
    const statusText = document.getElementById('statusText');
    const progressBar = document.getElementById('extractionProgress');
    const progressPercent = document.getElementById('progressPercent');
    const elapsedTime = document.getElementById('elapsedTime');
    const lastUpdated = document.getElementById('lastUpdated');
    const completionCard = document.getElementById('completionCard');
    const errorCard = document.getElementById('errorCard');
    const errorMessage = document.getElementById('errorMessage');
    const retryBtn = document.getElementById('retryBtn');
    const viewQuestionsBtn = document.getElementById('viewQuestionsBtn');
    
    // Status elements
    const statusElements = {
        'upload': {
            element: document.getElementById('uploadStatus'),
            icon: document.querySelector('#uploadStatus .status-icon i'),
            text: document.getElementById('uploadStatusText'),
            time: document.getElementById('uploadTime'),
            progress: null
        },
        'page_analysis': {
            element: document.getElementById('pageAnalysisStatus'),
            icon: document.querySelector('#pageAnalysisStatus .status-icon i'),
            text: document.getElementById('pageAnalysisText'),
            time: document.getElementById('pageAnalysisTime'),
            progress: {
                container: document.getElementById('pageAnalysisProgress'),
                bar: document.getElementById('pageProgressBar'),
                current: document.getElementById('pagesProcessed'),
                total: document.getElementById('totalPages'),
                percent: document.getElementById('pageProgressPercent')
            }
        },
        'extraction': {
            element: document.getElementById('extractionStatus'),
            icon: document.querySelector('#extractionStatus .status-icon i'),
            text: document.getElementById('extractionText'),
            time: document.getElementById('extractionTime'),
            progress: {
                container: document.getElementById('extractionProgressContainer'),
                count: document.getElementById('questionsFound')
            }
        },
        'saving': {
            element: document.getElementById('savingStatus'),
            icon: document.querySelector('#savingStatus .status-icon i'),
            text: document.getElementById('savingText'),
            time: document.getElementById('savingTime'),
            progress: null
        }
    };
    
    // Sidebar elements
    const sidebarElements = {
        pages: document.getElementById('sidebarPages'),
        questions: document.getElementById('sidebarQuestions'),
        status: document.getElementById('sidebarStatus')
    };
    
    // Document ID from template
    const documentId = '{{ document.id }}';
    const startTime = new Date();
    let checkInterval;
    let socket;
    let lastStatus = '';
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    const POLLING_INTERVAL = 3000; // 3 seconds
    const STATUS = {
        PENDING: 'pending',
        PROCESSING: 'processing',
        EXTRACTING: 'extracting',
        SAVING: 'saving',
        COMPLETED: 'completed',
        FAILED: 'failed'
    };
    
    /**
     * Initializes the extraction status page
     * - Sets up event listeners
     * - Initializes WebSocket connection
     * - Starts status polling
     * - Sets up the elapsed time counter
     * @memberof ExtractionStatus
     */
    function init() {
        // Set up retry button
        if (retryBtn) {
            retryBtn.addEventListener('click', function() {
                window.location.reload();
            });
        }
        
        // Initialize tooltips
        initTooltips();
        
        // Start WebSocket connection
        initWebSocket();
        
        // Start checking status via polling as fallback
        startPolling();
        
        // Update elapsed time every second
        setInterval(updateElapsedTime, 1000);
        
        // Initial UI update
        updateStatusUI(STATUS.PENDING, {
            message: 'Starting extraction process...',
            progress: 0
        });
    }
    
    /**
     * Initializes Bootstrap tooltips for elements with data-bs-toggle="tooltip"
     * @memberof ExtractionStatus
     */
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    /**
     * Starts polling for status updates at regular intervals
     * Used as a fallback when WebSockets are not available
     * @memberof ExtractionStatus
     */
    function startPolling() {
        // Initial check
        checkStatus();
        
        // Set up interval for polling
        checkInterval = setInterval(() => {
            // Only poll if WebSocket is not connected
            if (!socket || !socket.connected) {
                checkStatus();
            }
        }, POLLING_INTERVAL);
    }
    
    /**
     * Initializes WebSocket connection for real-time updates
     * Sets up event handlers for connection, disconnection, and errors
     * Falls back to polling if WebSocket connection fails
     * @memberof ExtractionStatus
     */
    function initWebSocket() {
        if (typeof io === 'undefined') {
            console.warn('Socket.IO not loaded, falling back to polling');
            return;
        }
        
        try {
            // Connect to the WebSocket server
            socket = io({
                path: '/socket.io',
                transports: ['websocket'],
                reconnectionAttempts: MAX_RECONNECT_ATTEMPTS,
                reconnectionDelay: 1000,
                timeout: 20000
            });
            
            // Connection established
            socket.on('connect', () => {
                console.log('Connected to WebSocket server');
                reconnectAttempts = 0;
                socket.emit('subscribe', { document_id: documentId });
                updateStatusUI(STATUS.PROCESSING, { message: 'Connected to real-time updates' });
            });
            
            // Handle status updates
            socket.on('status_update', (data) => {
                if (data.document_id === documentId) {
                    console.log('Received status update:', data);
                    updateUI(data);
                }
            });
            
            // Handle disconnection
            socket.on('disconnect', (reason) => {
                console.log('Disconnected from WebSocket:', reason);
                if (reason === 'io server disconnect') {
                    // Reconnect manually
                    socket.connect();
                }
            });
            
            // Handle connection errors
            socket.on('connect_error', (error) => {
                console.error('WebSocket connection error:', error);
                if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                    console.log(`Reconnecting in ${delay}ms...`);
                    setTimeout(() => {
                        reconnectAttempts++;
                        socket.connect();
                    }, delay);
                } else {
                    console.warn('Max reconnection attempts reached, falling back to polling');
                    updateStatusUI(STATUS.PROCESSING, { 
                        message: 'Using polling for updates (reconnect attempts exhausted)' 
                    });
                }
            });
            
            // Handle reconnection attempts
            socket.on('reconnect_attempt', (attempt) => {
                console.log(`Reconnection attempt ${attempt}/${MAX_RECONNECT_ATTEMPTS}`);
                updateStatusUI(STATUS.PROCESSING, { 
                    message: `Reconnecting to server (${attempt}/${MAX_RECONNECT_ATTEMPTS})...` 
                });
            });
            
            // Handle successful reconnection
            socket.on('reconnect', (attempt) => {
                console.log(`Successfully reconnected after ${attempt} attempts`);
                updateStatusUI(STATUS.PROCESSING, { message: 'Reconnected to server' });
                // Resubscribe to document updates
                socket.emit('subscribe', { document_id: documentId });
            });
            
        } catch (error) {
            console.error('Error initializing WebSocket:', error);
            updateStatusUI(STATUS.PROCESSING, { 
                message: 'Using polling for updates (WebSocket error)' 
            });
        }
    }
    
    /**
     * Updates the elapsed time counter
     * Called every second to show how long the extraction has been running
     * @memberof ExtractionStatus
     */
    function updateElapsedTime() {
        const now = new Date();
        const seconds = Math.floor((now - startTime) / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        if (elapsedTime) {
            elapsedTime.textContent = 
                `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        }
        
        // Update last updated time
        if (lastUpdated) {
            lastUpdated.textContent = `Last updated: ${formatTime(now)}`;
        }
    }
    
    /**
     * Formats a date object as HH:MM:SS
     * @param {Date} date - The date to format
     * @returns {string} Formatted time string
     * @memberof ExtractionStatus
     */
    function formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    }
    
    /**
     * Formats a date as a relative time string (e.g., '2 minutes ago')
     * @param {Date|string} date - The date to format
     * @returns {string} Relative time string
     * @memberof ExtractionStatus
     */
    function formatRelativeTime(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - new Date(date)) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }
    
    /**
     * Checks the current extraction status via AJAX
     * Used as a fallback when WebSockets are not available
     * @memberof ExtractionStatus
     */
    function checkStatus() {
        fetch(`/api/questions/${documentId}/status`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                updateUI(data);
            })
            .catch(error => {
                console.error('Error checking status:', error);
                // Only show error if we don't have a status yet or it's been a while
                if (!lastStatus || (Date.now() - lastStatusUpdate) > 30000) {
                    updateStatusUI(STATUS.FAILED, {
                        message: 'Error checking status. ' + (error.message || 'Please try again.')
                    });
                }
            });
    }
    
    // Track when we last received a status update
    let lastStatusUpdate = Date.now();
    let currentStatus = '';
    
    /**
     * Updates the UI based on the latest status data
     * @param {ExtractionStatusData} data - The status data from the server
     * @memberof ExtractionStatus
     */
    function updateUI(data) {
        if (!data) return;
        
        const status = data.status || 'pending';
        lastStatus = status;
        currentStatus = status;
        lastStatusUpdate = Date.now();
        
        // Update the main status UI
        updateStatusUI(status, data);
        
        // Update progress bar and other UI elements
        updateProgressUI(data);
        
        // Update sidebar with latest info
        updateSidebar(data);
        
        // Handle specific statuses
        switch (status) {
            case STATUS.COMPLETED:
                handleCompletion(data);
                break;
            case STATUS.FAILED:
                handleError(data);
                break;
            default:
                // For ongoing statuses, ensure completion/error cards are hidden
                if (completionCard) completionCard.style.display = 'none';
                if (errorCard) errorCard.style.display = 'none';
        }
    }
    
    /**
     * Updates the main status UI elements based on the current status
     * @param {string} status - The current status
     * @param {Object} [data={}] - Additional status data
     * @memberof ExtractionStatus
     */
    function updateStatusUI(status, data = {}) {
        const statusMessages = {
            [STATUS.PENDING]: 'Preparing to process document...',
            [STATUS.PROCESSING]: 'Analyzing document structure...',
            [STATUS.EXTRACTING]: 'Extracting questions from document...',
            [STATUS.SAVING]: 'Saving extracted questions...',
            [STATUS.COMPLETED]: 'Extraction completed successfully!',
            [STATUS.FAILED]: 'Extraction failed. ' + (data.message || 'An error occurred.')
        };
        
        // Update status text
        if (statusText) {
            statusText.textContent = statusMessages[status] || 'Processing...';
        }
        
        // Update status indicator in sidebar
        if (sidebarElements.status) {
            const statusClasses = {
                [STATUS.PENDING]: 'bg-secondary',
                [STATUS.PROCESSING]: 'bg-info',
                [STATUS.EXTRACTING]: 'bg-primary',
                [STATUS.SAVING]: 'bg-primary',
                [STATUS.COMPLETED]: 'bg-success',
                [STATUS.FAILED]: 'bg-danger'
            };
            
            const statusLabels = {
                [STATUS.PENDING]: 'Pending',
                [STATUS.PROCESSING]: 'Processing',
                [STATUS.EXTRACTING]: 'Extracting',
                [STATUS.SAVING]: 'Saving',
                [STATUS.COMPLETED]: 'Completed',
                [STATUS.FAILED]: 'Failed'
            };
            
            sidebarElements.status.className = `badge ${statusClasses[status] || 'bg-secondary'}`;
            sidebarElements.status.textContent = statusLabels[status] || 'Unknown';
        }
        
        // Update status cards
        updateStatusCards(status, data);
    }
    
    /**
     * Updates all status cards based on the current extraction status
     * @param {string} status - Current extraction status
     * @param {Object} data - Status data containing progress information
     * @memberof ExtractionStatus
     */
    function updateStatusCards(status, data) {
        // Reset all status cards first
        Object.values(statusElements).forEach(card => {
            if (card.element) {
                card.element.classList.remove('completed', 'in-progress', 'failed');
            }
            if (card.icon) {
                card.icon.classList.remove('text-success', 'text-primary', 'text-danger', 'text-muted');
                card.icon.classList.add('text-muted');
            }
        });
        
        // Update based on current status
        switch (status) {
            case STATUS.PROCESSING:
                updateStatusCard('upload', 'completed', 'Document uploaded successfully', true);
                updateStatusCard('page_analysis', 'in-progress', 'Analyzing document pages...', false);
                updateStatusCard('extraction', 'pending', 'Waiting for page analysis...', false);
                updateStatusCard('saving', 'pending', 'Waiting for extraction to complete...', false);
                break;
                
            case STATUS.EXTRACTING:
                updateStatusCard('upload', 'completed', 'Document uploaded successfully', true);
                updateStatusCard('page_analysis', 'completed', 'Page analysis complete', true);
                updateStatusCard('extraction', 'in-progress', 'Extracting questions...', false);
                updateStatusCard('saving', 'pending', 'Waiting for extraction to complete...', false);
                break;
                
            case STATUS.SAVING:
                updateStatusCard('upload', 'completed', 'Document uploaded successfully', true);
                updateStatusCard('page_analysis', 'completed', 'Page analysis complete', true);
                updateStatusCard('extraction', 'completed', 'Question extraction complete', true);
                updateStatusCard('saving', 'in-progress', 'Saving questions to database...', false);
                break;
                
            case STATUS.COMPLETED:
                updateStatusCard('upload', 'completed', 'Document uploaded successfully', true);
                updateStatusCard('page_analysis', 'completed', 'Page analysis complete', true);
                updateStatusCard('extraction', 'completed', 'Question extraction complete', true);
                updateStatusCard('saving', 'completed', 'Questions saved successfully', true);
                break;
                
            case STATUS.FAILED:
                // Mark all steps as failed or completed based on progress
                const failedStep = data.failed_step || 'processing';
                const steps = ['upload', 'page_analysis', 'extraction', 'saving'];
                let failedEncountered = false;
                
                steps.forEach(step => {
                    if (step === failedStep) {
                        updateStatusCard(step, 'failed', data.message || 'An error occurred', false);
                        failedEncountered = true;
                    } else if (failedEncountered) {
                        updateStatusCard(step, 'pending', 'Step skipped due to previous error', false);
                    } else {
                        updateStatusCard(step, 'completed', 'Step completed successfully', true);
                    }
                });
                break;
                
            default: // PENDING
                updateStatusCard('upload', 'in-progress', 'Uploading document...', false);
                updateStatusCard('page_analysis', 'pending', 'Waiting for upload to complete...', false);
                updateStatusCard('extraction', 'pending', 'Waiting for page analysis...', false);
                updateStatusCard('saving', 'pending', 'Waiting for extraction to complete...', false);
        }
        
        // Update timestamps
        if (data.timestamp) {
            const timeStr = formatTime(new Date(data.timestamp));
            switch (status) {
                case STATUS.PROCESSING:
                    updateStatusTime('page_analysis', timeStr);
                    break;
                case STATUS.EXTRACTING:
                    updateStatusTime('extraction', timeStr);
                    break;
                case STATUS.SAVING:
                    updateStatusTime('saving', timeStr);
                    break;
                case STATUS.COMPLETED:
                case STATUS.FAILED:
                    updateStatusTime('saving', timeStr);
                    break;
            }
        }
    }
    
    /**
     * Updates a single status card with the given status and message
     * @param {string} type - Type of status card ('upload', 'page_analysis', 'extraction', 'saving')
     * @param {string} status - Status to set ('completed', 'in-progress', 'failed', 'pending')
     * @param {string} message - Status message to display
     * @param {boolean} [isComplete] - Whether the status represents a completed state
     * @memberof ExtractionStatus
     */
    function updateStatusCard(type, status, message, isComplete) {
        const card = statusElements[type];
        if (!card || !card.element) return;
        
        // Update card classes
        card.element.classList.remove('completed', 'in-progress', 'failed', 'pending');
        card.element.classList.add(status);
        
        // Update icon
        if (card.icon) {
            card.icon.classList.remove('text-success', 'text-primary', 'text-danger', 'text-muted');
            
            switch (status) {
                case 'completed':
                    card.icon.classList.add('text-success');
                    card.icon.setAttribute('data-feather', 'check-circle');
                    break;
                case 'in-progress':
                    card.icon.classList.add('text-primary');
                    card.icon.setAttribute('data-feather', 'loader');
                    card.icon.classList.add('spin');
                    break;
                case 'failed':
                    card.icon.classList.add('text-danger');
                    card.icon.setAttribute('data-feather', 'alert-circle');
                    break;
                default: // pending
                    card.icon.classList.add('text-muted');
                    card.icon.setAttribute('data-feather', 'clock');
            }
            
            // Refresh Feather icon
            if (window.feather) {
                window.feather.replace({ class: 'feather-icon' });
            }
        }
        
        // Update text
        if (card.text) {
            card.text.textContent = message;
        }
        
        // Update progress indicators if they exist
        if (card.progress) {
            if (status === 'in-progress') {
                if (card.progress.container) card.progress.container.style.display = 'block';
            } else {
                if (card.progress.container) card.progress.container.style.display = 'none';
            }
        }
    }
    
    /**
     * Updates the timestamp for a status element
     * @param {string} type - Type of status element to update
     * @param {string} timeStr - Formatted time string to display
     * @memberof ExtractionStatus
     */
    function updateStatusTime(type, timeStr) {
        const card = statusElements[type];
        if (card && card.time) {
            card.time.textContent = timeStr;
        }
    }
    
    /**
     * Updates all progress-related UI elements
     * @param {ExtractionStatusData} data - Status data containing progress information
     * @memberof ExtractionStatus
     */
    function updateProgressUI(data) {
        const progress = data.progress || 0;
        
        // Update main progress bar
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
            
            // Update progress percentage text
            if (progressPercent) {
                progressPercent.textContent = `${Math.round(progress)}%`;
            }
            
            // Update progress bar color based on status
            progressBar.classList.remove('bg-success', 'bg-warning', 'bg-danger', 'bg-info', 'bg-primary');
            
            switch (currentStatus) {
                case STATUS.COMPLETED:
                    progressBar.classList.add('bg-success');
                    break;
                case STATUS.FAILED:
                    progressBar.classList.add('bg-danger');
                    break;
                case STATUS.PROCESSING:
                    progressBar.classList.add('bg-info');
                    break;
                case STATUS.EXTRACTING:
                case STATUS.SAVING:
                    progressBar.classList.add('bg-primary');
                    break;
                default:
                    progressBar.classList.add('bg-secondary');
            }
        }
        
        // Update page analysis progress if data is available
        if (data.page_analysis && statusElements.page_analysis && statusElements.page_analysis.progress) {
            const pa = statusElements.page_analysis.progress;
            const current = data.page_analysis.current_page || 0;
            const total = data.page_analysis.total_pages || 1;
            const pageProgress = Math.round((current / total) * 100);
            
            if (pa.current) pa.current.textContent = current;
            if (pa.total) pa.total.textContent = total;
            if (pa.percent) pa.percent.textContent = `${pageProgress}%`;
            if (pa.bar) {
                pa.bar.style.width = `${pageProgress}%`;
                pa.bar.setAttribute('aria-valuenow', pageProgress);
            }
            
            // Update sidebar pages
            if (sidebarElements.pages) {
                sidebarElements.pages.textContent = `${current} / ${total}`;
            }
        }
        
        // Update questions found if data is available
        if (data.questions_extracted !== undefined && statusElements.extraction && statusElements.extraction.progress) {
            const count = data.questions_extracted;
            const ext = statusElements.extraction.progress;
            
            if (ext.count) ext.count.textContent = count;
            
            // Update sidebar questions
            if (sidebarElements.questions) {
                sidebarElements.questions.textContent = count;
            }
        }
    }
    
    /**
     * Updates the sidebar with document information
     * @param {ExtractionStatusData} data - Status data containing document information
     * @memberof ExtractionStatus
     */
    function updateSidebar(data) {
        if (!data) return;
        
        // Update pages if available
        if (data.page_analysis && sidebarElements.pages) {
            const current = data.page_analysis.current_page || 0;
            const total = data.page_analysis.total_pages || 0;
            sidebarElements.pages.textContent = total > 0 ? `${current} / ${total}` : '0';
        }
        
        // Update questions if available
        if (data.questions_extracted !== undefined && sidebarElements.questions) {
            sidebarElements.questions.textContent = data.questions_extracted || '0';
        }
    }
    
    /**
     * Handles the completion of the extraction process
     * - Stops polling/WebSocket updates
     * - Updates UI to show completion state
     * - Enables navigation to view extracted questions
     * @param {ExtractionStatusData} data - Completion status data
     * @memberof ExtractionStatus
     */
    function handleCompletion(data) {
        // Stop polling when completed
        if (checkInterval) {
            clearInterval(checkInterval);
            checkInterval = null;
        }
        
        // Show completion card
        if (completionCard) {
            completionCard.style.display = 'block';
            
            // Update question count if available
            const questionCount = document.getElementById('questionCount');
            if (questionCount && data.questions_extracted !== undefined) {
                questionCount.textContent = data.questions_extracted;
            }
            
            // Update view questions button
            if (viewQuestionsBtn) {
                viewQuestionsBtn.href = `/questions/${documentId}`;
            }
        }
        
        // Hide error card if shown
        if (errorCard) {
            errorCard.style.display = 'none';
        }
    }
    
    /**
     * Handles extraction errors
     * - Stops polling/WebSocket updates
     * - Displays error message to the user
     * - Enables retry functionality
     * @param {ExtractionStatusData} data - Error status data
     * @memberof ExtractionStatus
     */
    function handleError(data) {
        // Stop polling when failed
        if (checkInterval) {
            clearInterval(checkInterval);
            checkInterval = null;
        }
        
        // Show error card
        if (errorCard) {
            errorCard.style.display = 'block';
            
            // Update error message
            if (errorMessage) {
                let message = 'An error occurred during the extraction process.';
                if (data.message) {
                    message = data.message;
                } else if (data.error) {
                    message = data.error;
                }
                errorMessage.textContent = message;
            }
            
            // Update retry button
            if (retryBtn) {
                retryBtn.onclick = function() {
                    window.location.reload();
                };
            }
        }
        
        // Hide completion card if shown
        if (completionCard) {
            completionCard.style.display = 'none';
        }
    }
    
    /**
     * Initialize the extraction status application
     * This is the entry point that starts the entire process
     */
    init();
});

// End of extraction_status.js
