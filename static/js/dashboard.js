// ResearchNest Admin Dashboard JavaScript
// Handles analytics charts and dashboard interactions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all dashboard components
    initializeCharts();
    initializeRealTimeUpdates();
    initializeDashboardInteractions();
});

let chartsData = {}; // Store chart instances for updates

function initializeCharts() {
    // Initialize all charts
    loadPapersByDepartmentChart();
    loadTrendsChart();
    loadKeywordsChart();
}

function loadPapersByDepartmentChart() {
    const ctx = document.getElementById('departmentChart');
    if (!ctx) return;

    fetch('/api/analytics/papers-by-department')
        .then(response => response.json())
        .then(data => {
            const chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(255, 205, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(153, 102, 255, 0.8)',
                            'rgba(255, 159, 64, 0.8)',
                            'rgba(199, 199, 199, 0.8)',
                            'rgba(83, 102, 255, 0.8)',
                            'rgba(255, 99, 255, 0.8)',
                            'rgba(99, 255, 132, 0.8)'
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(255, 205, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(199, 199, 199, 1)',
                            'rgba(83, 102, 255, 1)',
                            'rgba(255, 99, 255, 1)',
                            'rgba(99, 255, 132, 1)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true,
                                color: getComputedStyle(document.documentElement).getPropertyValue('--bs-body-color')
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value} papers (${percentage}%)`;
                                }
                            }
                        }
                    },
                    animation: {
                        animateRotate: true,
                        duration: 1000
                    }
                }
            });
            
            chartsData.departmentChart = chart;
        })
        .catch(error => {
            console.error('Error loading department chart:', error);
            showChartError('departmentChart', 'Failed to load department data');
        });
}

function loadTrendsChart() {
    const ctx = document.getElementById('trendsChart');
    if (!ctx) return;

    Promise.all([
        fetch('/api/analytics/uploads-by-month').then(r => r.json()),
        fetch('/api/analytics/downloads-by-month').then(r => r.json())
    ])
    .then(([uploadsData, downloadsData]) => {
        // Merge and align the data by month
        const allMonths = new Set([...uploadsData.labels, ...downloadsData.labels]);
        const sortedMonths = Array.from(allMonths).sort();
        
        const uploads = sortedMonths.map(month => {
            const index = uploadsData.labels.indexOf(month);
            return index !== -1 ? uploadsData.data[index] : 0;
        });
        
        const downloads = sortedMonths.map(month => {
            const index = downloadsData.labels.indexOf(month);
            return index !== -1 ? downloadsData.data[index] : 0;
        });

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: sortedMonths,
                datasets: [
                    {
                        label: 'Uploads',
                        data: uploads,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                        pointBorderWidth: 2,
                        pointRadius: 6
                    },
                    {
                        label: 'Downloads',
                        data: downloads,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                        pointBorderWidth: 2,
                        pointRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            color: getComputedStyle(document.documentElement).getPropertyValue('--bs-body-color')
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        callbacks: {
                            title: function(context) {
                                return `Month: ${context[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--bs-body-color')
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--bs-body-color'),
                            stepSize: 1
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        });
        
        chartsData.trendsChart = chart;
    })
    .catch(error => {
        console.error('Error loading trends chart:', error);
        showChartError('trendsChart', 'Failed to load trends data');
    });
}

function loadKeywordsChart() {
    const ctx = document.getElementById('keywordsChart');
    if (!ctx) return;

    fetch('/api/analytics/top-keywords')
        .then(response => response.json())
        .then(data => {
            if (data.labels.length === 0) {
                showChartError('keywordsChart', 'No keywords data available');
                return;
            }

            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Frequency',
                        data: data.data,
                        backgroundColor: 'rgba(153, 102, 255, 0.8)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 2,
                        borderRadius: 4,
                        borderSkipped: false,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                            borderWidth: 1,
                            callbacks: {
                                label: function(context) {
                                    return `Used ${context.parsed.x} times`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: getComputedStyle(document.documentElement).getPropertyValue('--bs-body-color'),
                                stepSize: 1
                            }
                        },
                        y: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: getComputedStyle(document.documentElement).getPropertyValue('--bs-body-color'),
                                font: {
                                    size: 11
                                }
                            }
                        }
                    },
                    animation: {
                        duration: 1200,
                        easing: 'easeOutBounce'
                    }
                }
            });
            
            chartsData.keywordsChart = chart;
        })
        .catch(error => {
            console.error('Error loading keywords chart:', error);
            showChartError('keywordsChart', 'Failed to load keywords data');
        });
}

function showChartError(chartId, message) {
    const canvas = document.getElementById(chartId);
    if (!canvas) return;
    
    const container = canvas.parentNode;
    container.innerHTML = `
        <div class="text-center py-4">
            <i data-feather="alert-circle" class="display-4 text-muted mb-3"></i>
            <p class="text-muted">${message}</p>
            <button class="btn btn-outline-secondary btn-sm" onclick="location.reload()">
                <i data-feather="refresh-cw" class="me-1"></i>Retry
            </button>
        </div>
    `;
    feather.replace();
}

function initializeRealTimeUpdates() {
    // Auto-refresh dashboard data every 5 minutes
    setInterval(() => {
        updateDashboardStats();
        refreshCharts();
    }, 5 * 60 * 1000);
}

function updateDashboardStats() {
    // Update the stat cards without full page reload
    // This would typically fetch updated stats from an API endpoint
    const statCards = document.querySelectorAll('.card.bg-primary, .card.bg-success, .card.bg-info, .card.bg-warning');
    
    statCards.forEach(card => {
        card.style.opacity = '0.7';
        setTimeout(() => {
            card.style.opacity = '1';
        }, 1000);
    });
}

function refreshCharts() {
    // Refresh all charts with new data
    Object.keys(chartsData).forEach(chartKey => {
        const chart = chartsData[chartKey];
        if (chart) {
            // Add a subtle loading indicator
            chart.canvas.style.opacity = '0.7';
            
            setTimeout(() => {
                chart.canvas.style.opacity = '1';
            }, 1000);
        }
    });
}

function initializeDashboardInteractions() {
    // Add click interactions to stat cards
    initializeStatCardInteractions();
    
    // Add chart interaction handlers
    initializeChartInteractions();
    
    // Add quick action buttons
    initializeQuickActions();
    
    // Add keyboard shortcuts
    initializeKeyboardShortcuts();
}

function initializeStatCardInteractions() {
    const statCards = document.querySelectorAll('.card.bg-primary, .card.bg-success, .card.bg-info, .card.bg-warning');
    
    statCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            const cardText = this.querySelector('.card-text').textContent.toLowerCase();
            
            if (cardText.includes('papers')) {
                window.location.href = '/admin/papers';
            } else if (cardText.includes('users')) {
                window.location.href = '/admin/users';
            } else if (cardText.includes('downloads')) {
                window.location.href = '/search';
            } else if (cardText.includes('pending')) {
                window.location.href = '/admin/papers?status=pending';
            }
        });
        
        // Add hover effect
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function initializeChartInteractions() {
    // Add export functionality to charts
    addChartExportButtons();
    
    // Add drill-down functionality
    addChartDrillDown();
}

function addChartExportButtons() {
    const chartContainers = document.querySelectorAll('.card .card-body canvas');
    
    chartContainers.forEach(canvas => {
        const cardHeader = canvas.closest('.card').querySelector('.card-header');
        if (!cardHeader) return;
        
        const exportBtn = document.createElement('button');
        exportBtn.className = 'btn btn-outline-secondary btn-sm float-end';
        exportBtn.innerHTML = '<i data-feather="download"></i>';
        exportBtn.title = 'Export Chart';
        
        exportBtn.addEventListener('click', function() {
            exportChart(canvas);
        });
        
        cardHeader.appendChild(exportBtn);
    });
    
    feather.replace();
}

function exportChart(canvas) {
    const link = document.createElement('a');
    link.download = `chart-${Date.now()}.png`;
    link.href = canvas.toDataURL();
    link.click();
}

function addChartDrillDown() {
    // Add click handlers to charts for drill-down functionality
    if (chartsData.departmentChart) {
        chartsData.departmentChart.canvas.addEventListener('click', function(evt) {
            const points = chartsData.departmentChart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
            
            if (points.length) {
                const firstPoint = points[0];
                const label = chartsData.departmentChart.data.labels[firstPoint.index];
                
                // Navigate to papers filtered by department
                window.location.href = `/search?department=${encodeURIComponent(label)}`;
            }
        });
    }
}

function initializeQuickActions() {
    // Add quick action functionality
    const quickActionBtns = document.querySelectorAll('.card .btn');
    
    quickActionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Add loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i data-feather="loader" class="me-1"></i>Loading...';
            this.disabled = true;
            
            feather.replace();
            
            // Re-enable after navigation (or timeout)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
                feather.replace();
            }, 2000);
        });
    });
}

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Only activate shortcuts when not typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }
        
        // Ctrl/Cmd + key combinations
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'p':
                    e.preventDefault();
                    window.location.href = '/admin/papers';
                    break;
                case 'u':
                    e.preventDefault();
                    window.location.href = '/admin/users';
                    break;
                case 'r':
                    e.preventDefault();
                    location.reload();
                    break;
            }
        }
        
        // Single key shortcuts
        switch(e.key) {
            case 'h':
                window.location.href = '/';
                break;
            case 's':
                window.location.href = '/search';
                break;
        }
    });
}

// Utility functions for dashboard
function animateCounter(element, target, duration = 1000) {
    const start = parseInt(element.textContent) || 0;
    const range = target - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Initialize counter animations on page load
document.addEventListener('DOMContentLoaded', function() {
    const counters = document.querySelectorAll('.card-title');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent);
        if (!isNaN(target)) {
            counter.textContent = '0';
            setTimeout(() => {
                animateCounter(counter, target);
            }, 500);
        }
    });
});
