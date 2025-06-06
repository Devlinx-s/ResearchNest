// ResearchNest Search Page JavaScript
// Handles search functionality, filters, and result interactions

document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const clearFiltersBtn = document.getElementById('clearFilters');
    const clearAllFiltersBtn = document.getElementById('clearAllFilters');
    const queryInput = document.querySelector('input[name="query"]');
    
    // Initialize search functionality
    initializeSearch();
    initializeClearButtons();
    initializeAdvancedFilters();
    initializeResultInteractions();
    
    function initializeSearch() {
        if (!searchForm) return;

        // Auto-submit on filter change (with debounce)
        let searchTimeout;
        const formInputs = searchForm.querySelectorAll('input, select');
        
        formInputs.forEach(input => {
            if (input.type === 'submit') return;
            
            input.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    if (shouldAutoSubmit(input)) {
                        submitSearch();
                    }
                }, 500);
            });
            
            if (input.tagName === 'SELECT') {
                input.addEventListener('change', function() {
                    submitSearch();
                });
            }
        });

        // Handle form submission
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitSearch();
        });

        // Search suggestions (simple implementation)
        if (queryInput) {
            initializeSearchSuggestions();
        }
    }

    function shouldAutoSubmit(input) {
        // Only auto-submit for certain fields to avoid too many requests
        return ['department_id', 'year_from', 'year_to'].includes(input.name);
    }

    function submitSearch() {
        // Add loading state
        showSearchLoading(true);
        
        // Manually submit the form
        const formData = new FormData(searchForm);
        const params = new URLSearchParams();
        
        for (let [key, value] of formData.entries()) {
            if (value.trim()) {
                params.append(key, value);
            }
        }
        
        // Update URL and reload
        const newUrl = window.location.pathname + '?' + params.toString();
        window.location.href = newUrl;
    }

    function initializeClearButtons() {
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', function() {
                clearAllFormFields();
                submitSearch();
            });
        }

        if (clearAllFiltersBtn) {
            clearAllFiltersBtn.addEventListener('click', function() {
                clearAllFormFields();
                submitSearch();
            });
        }
    }

    function clearAllFormFields() {
        if (!searchForm) return;

        const inputs = searchForm.querySelectorAll('input[type="text"], input[type="number"]');
        const selects = searchForm.querySelectorAll('select');
        
        inputs.forEach(input => {
            input.value = '';
        });
        
        selects.forEach(select => {
            select.selectedIndex = 0;
        });
    }

    function initializeAdvancedFilters() {
        // Year range validation
        const yearFromInput = document.querySelector('input[name="year_from"]');
        const yearToInput = document.querySelector('input[name="year_to"]');
        
        if (yearFromInput && yearToInput) {
            yearFromInput.addEventListener('change', function() {
                validateYearRange();
            });
            
            yearToInput.addEventListener('change', function() {
                validateYearRange();
            });
        }

        // Keywords input enhancement
        const keywordsInput = document.querySelector('input[name="keywords"]');
        if (keywordsInput) {
            initializeKeywordsInput(keywordsInput);
        }
    }

    function validateYearRange() {
        const yearFromInput = document.querySelector('input[name="year_from"]');
        const yearToInput = document.querySelector('input[name="year_to"]');
        
        if (!yearFromInput || !yearToInput) return;

        const yearFrom = parseInt(yearFromInput.value);
        const yearTo = parseInt(yearToInput.value);
        
        if (yearFrom && yearTo && yearFrom > yearTo) {
            yearToInput.setCustomValidity('End year must be greater than or equal to start year');
            yearToInput.classList.add('is-invalid');
        } else {
            yearToInput.setCustomValidity('');
            yearToInput.classList.remove('is-invalid');
        }
    }

    function initializeKeywordsInput(input) {
        // Add visual feedback for comma-separated keywords
        input.addEventListener('input', function() {
            const value = this.value;
            const keywords = value.split(',').map(k => k.trim()).filter(k => k);
            
            // Show keyword count
            updateKeywordCount(keywords.length);
        });

        // Add keyword suggestions
        createKeywordSuggestions(input);
    }

    function updateKeywordCount(count) {
        const keywordsInput = document.querySelector('input[name="keywords"]');
        if (!keywordsInput) return;

        let counter = keywordsInput.parentNode.querySelector('.keyword-counter');
        if (!counter) {
            counter = document.createElement('small');
            counter.className = 'keyword-counter form-text text-muted';
            keywordsInput.parentNode.appendChild(counter);
        }
        
        if (count > 0) {
            counter.textContent = `${count} keyword${count !== 1 ? 's' : ''}`;
        } else {
            counter.textContent = '';
        }
    }

    function createKeywordSuggestions(input) {
        // This would typically fetch from an API
        const commonKeywords = [
            'artificial intelligence', 'machine learning', 'data science',
            'computer vision', 'natural language processing', 'deep learning',
            'algorithms', 'software engineering', 'cybersecurity', 'blockchain',
            'robotics', 'virtual reality', 'augmented reality', 'IoT',
            'cloud computing', 'mobile development', 'web development'
        ];

        const suggestionsList = document.createElement('div');
        suggestionsList.className = 'keyword-suggestions';
        suggestionsList.style.display = 'none';
        input.parentNode.appendChild(suggestionsList);

        input.addEventListener('focus', function() {
            showKeywordSuggestions(suggestionsList, commonKeywords, input);
        });

        input.addEventListener('blur', function() {
            // Hide suggestions after a brief delay to allow clicking
            setTimeout(() => {
                suggestionsList.style.display = 'none';
            }, 200);
        });
    }

    function showKeywordSuggestions(container, keywords, input) {
        const currentValue = input.value.toLowerCase();
        const currentKeywords = currentValue.split(',').map(k => k.trim());
        const lastKeyword = currentKeywords[currentKeywords.length - 1];

        const filteredKeywords = keywords.filter(keyword => 
            keyword.toLowerCase().includes(lastKeyword) && 
            !currentKeywords.includes(keyword)
        ).slice(0, 5);

        if (filteredKeywords.length === 0) {
            container.style.display = 'none';
            return;
        }

        container.innerHTML = filteredKeywords.map(keyword => 
            `<div class="suggestion-item p-2 border-bottom cursor-pointer">${keyword}</div>`
        ).join('');

        container.style.display = 'block';
        container.style.position = 'absolute';
        container.style.background = 'var(--bs-body-bg)';
        container.style.border = '1px solid var(--bs-border-color)';
        container.style.borderRadius = '0.375rem';
        container.style.maxHeight = '200px';
        container.style.overflowY = 'auto';
        container.style.width = input.offsetWidth + 'px';
        container.style.zIndex = '1000';

        // Add click handlers
        container.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', function() {
                addKeywordToInput(input, this.textContent);
                container.style.display = 'none';
            });
        });
    }

    function addKeywordToInput(input, keyword) {
        const currentValue = input.value;
        const keywords = currentValue.split(',').map(k => k.trim());
        
        // Replace the last keyword (which was being typed)
        keywords[keywords.length - 1] = keyword;
        
        input.value = keywords.join(', ') + ', ';
        input.focus();
    }

    function initializeSearchSuggestions() {
        // Simple search suggestions based on recent searches or popular terms
        const suggestionsList = createSearchSuggestionsList();
        
        queryInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length > 2) {
                showSearchSuggestions(suggestionsList, query);
            } else {
                hideSuggestions(suggestionsList);
            }
        });

        queryInput.addEventListener('blur', function() {
            setTimeout(() => hideSuggestions(suggestionsList), 200);
        });
    }

    function createSearchSuggestionsList() {
        const suggestions = document.createElement('div');
        suggestions.className = 'search-suggestions';
        suggestions.style.display = 'none';
        queryInput.parentNode.appendChild(suggestions);
        return suggestions;
    }

    function showSearchSuggestions(container, query) {
        // This would typically fetch from an API
        const suggestions = generateSearchSuggestions(query);
        
        if (suggestions.length === 0) {
            hideSuggestions(container);
            return;
        }

        container.innerHTML = suggestions.map(suggestion => 
            `<div class="suggestion-item p-2 border-bottom cursor-pointer">
                <i data-feather="search" class="me-2"></i>${suggestion}
            </div>`
        ).join('');

        container.style.display = 'block';
        container.style.position = 'absolute';
        container.style.background = 'var(--bs-body-bg)';
        container.style.border = '1px solid var(--bs-border-color)';
        container.style.borderRadius = '0.375rem';
        container.style.width = queryInput.offsetWidth + 'px';
        container.style.zIndex = '1000';

        // Replace feather icons
        feather.replace();

        // Add click handlers
        container.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', function() {
                queryInput.value = this.textContent.trim();
                hideSuggestions(container);
                submitSearch();
            });
        });
    }

    function hideSuggestions(container) {
        container.style.display = 'none';
    }

    function generateSearchSuggestions(query) {
        // Simple suggestion generation - in real app, this would be from API
        const suggestions = [];
        const lowerQuery = query.toLowerCase();
        
        // Add "Search for..." suggestion
        suggestions.push(`Search for "${query}"`);
        
        // Add field-specific suggestions
        if (lowerQuery.includes('ai') || lowerQuery.includes('artificial')) {
            suggestions.push('artificial intelligence papers');
        }
        if (lowerQuery.includes('machine') || lowerQuery.includes('ml')) {
            suggestions.push('machine learning research');
        }
        if (lowerQuery.includes('data')) {
            suggestions.push('data science studies');
        }
        
        return suggestions.slice(0, 5);
    }

    function initializeResultInteractions() {
        // Add keyboard navigation for search results
        const resultCards = document.querySelectorAll('.papers-list .card');
        
        resultCards.forEach((card, index) => {
            card.setAttribute('tabindex', '0');
            card.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    const viewLink = card.querySelector('a[href*="paper_detail"]');
                    if (viewLink) {
                        viewLink.click();
                    }
                }
            });
        });

        // Add result highlighting on hover
        resultCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });

        // Initialize copy to clipboard for paper URLs
        initializeCopyButtons();
    }

    function initializeCopyButtons() {
        const copyButtons = document.querySelectorAll('[data-copy-url]');
        
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const url = this.getAttribute('data-copy-url');
                copyToClipboard(url);
                showCopyFeedback(this);
            });
        });
    }

    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
    }

    function showCopyFeedback(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i data-feather="check" class="me-1"></i>Copied!';
        button.classList.add('btn-success');
        button.classList.remove('btn-outline-secondary');
        
        feather.replace();
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-secondary');
            feather.replace();
        }, 2000);
    }

    function showSearchLoading(show) {
        const searchButton = searchForm.querySelector('button[type="submit"]');
        
        if (show) {
            searchButton.disabled = true;
            searchButton.innerHTML = '<i data-feather="loader" class="me-1"></i>Searching...';
        } else {
            searchButton.disabled = false;
            searchButton.innerHTML = '<i data-feather="search" class="me-1"></i>Search';
        }
        
        feather.replace();
    }

    // Save search state to localStorage for better UX
    function saveSearchState() {
        const formData = new FormData(searchForm);
        const searchState = {};
        
        for (let [key, value] of formData.entries()) {
            if (value.trim()) {
                searchState[key] = value;
            }
        }
        
        localStorage.setItem('researchNestSearchState', JSON.stringify(searchState));
    }

    function loadSearchState() {
        try {
            const savedState = localStorage.getItem('researchNestSearchState');
            if (savedState) {
                const searchState = JSON.parse(savedState);
                
                Object.keys(searchState).forEach(key => {
                    const input = searchForm.querySelector(`[name="${key}"]`);
                    if (input) {
                        input.value = searchState[key];
                    }
                });
            }
        } catch (e) {
            console.error('Error loading search state:', e);
        }
    }

    // Save search state on form changes
    if (searchForm) {
        searchForm.addEventListener('change', saveSearchState);
    }
});
