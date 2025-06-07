// Gaming Analytics Dashboard JavaScript

// Global variables for chart data (will be populated from server)
let stats, topGames, platformCounts, genreCounts, gamesPerYear, publisherCounts;
let avgRatingPlatform, avgRatingDeveloper, directorAnalytics, gameTypeDistribution;
let ratingDistribution, votesAnalytics, mostVotedGames, collectionSummary;
let recentReleases, ratingTrends, monthlyActivity, platformPerformance, topRatedRecent;
let tacticalSankeyData, tacticalVennData, tacticalChordData, tacticalDumbbellData, tacticalMarimekkoData;
let lifecycleSurvivalData, lifecycleRidgelineData, lifecycleTimelineData, lifecycleHexbinData, lifecycleParallelData;
let evolutionStreamData, evolutionBubbleData, evolutionHexbinData, evolutionParallelData, evolutionTreeData;

// Utility Functions
function filterUnwantedValues(data, labelKey = '_id', valueKey = 'count') {
    const unwantedValues = [
        'other', 'null', '', 'undefined', 'none', 'n/a', 'unknown', 
        'not specified', 'not available', 'various', 'misc', 'miscellaneous',
        'tbd', 'tba', 'to be announced', 'to be determined', 'missing'
    ];
    
    return data.filter(item => {
        const label = item[labelKey];
        if (!label) return false;
        
        const labelStr = String(label).toLowerCase().trim();
        return !unwantedValues.includes(labelStr) && labelStr.length > 0;
    });
}

function generateColors(num) {
    const colorPalette = [
        '#50fa7b', '#ff79c6', '#8be9fd', '#ffb86c', '#bd93f9',
        '#f1fa8c', '#ff5555', '#6272a4', '#44475a', '#282a36',
        '#00ff41', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4',
        '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3'
    ];
    return colorPalette.slice(0, num);
}

// Common chart options
const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
        duration: 1000
    },
    plugins: {
        legend: {
            labels: { 
                color: '#eee',
                font: {
                    family: 'Roboto',
                    size: 11
                }
            }
        },
        title: { 
            color: '#e94560',
            font: {
                family: 'Orbitron',
                size: 12,
                weight: 'bold'
            }
        }
    },
    scales: {
        x: { 
            ticks: { 
                color: '#eee',
                font: {
                    family: 'Roboto',
                    size: 10
                }
            }, 
            grid: { color: '#0f3460' } 
        },
        y: { 
            beginAtZero: true, 
            ticks: { 
                color: '#eee',
                font: {
                    family: 'Roboto',
                    size: 10
                }
            }, 
            grid: { color: '#0f3460' } 
        }
    }
};

// Enhanced Dashboard Management Class
class DashboardManager {
    constructor() {
        this.activeTab = 'studio';
        this.initializeEventListeners();
        this.initializeFilters();
    }

    initializeEventListeners() {
        // Listen for Bootstrap tab events instead of click events
        document.querySelectorAll('.nav-link[data-tab]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const tabName = e.target.getAttribute('data-tab');
                this.handleTabSwitch(tabName);
            });
        });

        // Filter form submissions
        document.querySelectorAll('form[id$="-filter-form"]').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFilterSubmit(e);
            });
        });

        // Reset button handlers
        document.querySelectorAll('button[id^="reset-"]').forEach(button => {
            button.addEventListener('click', (e) => {
                this.resetFilters(e.target.id.replace('reset-', '').replace('-filters', ''));
            });
        });

        // Range slider updates
        this.initializeRangeSliders();
    }

    initializeFilters() {
        // Initialize tactical dashboard specific filters
        this.initializeTacticalFilters();
        
        // Show appropriate filter section based on current tab
        this.showFilterSection(this.activeTab);
    }

    initializeTacticalFilters() {
        // Year range sliders for tactical dashboard
        const tacticalYearStart = document.getElementById('tactical-year-start');
        const tacticalYearEnd = document.getElementById('tactical-year-end');
        const tacticalYearDisplay = document.getElementById('tactical-year-range-display');

        if (tacticalYearStart && tacticalYearEnd && tacticalYearDisplay) {
            const updateTacticalYearDisplay = () => {
                const startYear = parseInt(tacticalYearStart.value);
                const endYear = parseInt(tacticalYearEnd.value);
                
                // Ensure start year is not greater than end year
                if (startYear > endYear) {
                    tacticalYearStart.value = endYear;
                }
                if (endYear < startYear) {
                    tacticalYearEnd.value = startYear;
                }
                
                tacticalYearDisplay.textContent = `${tacticalYearStart.value} - ${tacticalYearEnd.value}`;
            };

            tacticalYearStart.addEventListener('input', updateTacticalYearDisplay);
            tacticalYearEnd.addEventListener('input', updateTacticalYearDisplay);
            
            // Initialize display
            updateTacticalYearDisplay();
        }

        // Platform and genre quick selection buttons
        this.setupQuickSelectionButtons();
    }

    setupQuickSelectionButtons() {
        // Major platforms selection
        window.selectMajorPlatforms = () => {
            const platformSelect = document.getElementById('tactical-platform-filter');
            if (platformSelect) {
                const majorPlatforms = ['PC', 'PlayStation', 'PlayStation 2', 'PlayStation 3', 'PlayStation 4', 'Xbox', 'Xbox 360', 'Xbox One', 'Nintendo Switch', 'Nintendo DS'];
                Array.from(platformSelect.options).forEach(option => {
                    option.selected = majorPlatforms.some(platform => option.value.includes(platform));
                });
            }
        };

        // Clear platform selection
        window.clearPlatformSelection = () => {
            const platformSelect = document.getElementById('tactical-platform-filter');
            if (platformSelect) {
                Array.from(platformSelect.options).forEach(option => {
                    option.selected = false;
                });
            }
        };

        // Popular genres selection
        window.selectPopularGenres = () => {
            const genreSelect = document.getElementById('tactical-genre-filter');
            if (genreSelect) {
                const popularGenres = ['Action', 'Adventure', 'Role-Playing', 'Strategy', 'Simulation', 'Sports', 'Racing', 'Shooter'];
                Array.from(genreSelect.options).forEach(option => {
                    option.selected = popularGenres.includes(option.value);
                });
            }
        };

        // Clear genre selection
        window.clearGenreSelection = () => {
            const genreSelect = document.getElementById('tactical-genre-filter');
            if (genreSelect) {
                Array.from(genreSelect.options).forEach(option => {
                    option.selected = false;
                });
            }
        };

        // Evolution dashboard genre selection
        window.selectEvolutionGenres = () => {
            const genreSelect = document.getElementById('evolution-genre-filter');
            if (genreSelect) {
                const coreGenres = ['Action', 'Adventure', 'Role-Playing', 'Strategy', 'Simulation', 'Puzzle'];
                Array.from(genreSelect.options).forEach(option => {
                    option.selected = coreGenres.includes(option.value);
                });
            }
        };

        // Clear evolution genres
        window.clearEvolutionGenres = () => {
            const genreSelect = document.getElementById('evolution-genre-filter');
            if (genreSelect) {
                Array.from(genreSelect.options).forEach(option => {
                    option.selected = false;
                });
            }
        };
    }

    initializeRangeSliders() {
        // Studio Performance year range sliders
        const yearStart = document.getElementById('year-start');
        const yearEnd = document.getElementById('year-end');
        const yearDisplay = document.getElementById('year-range-display');

        if (yearStart && yearEnd && yearDisplay) {
            const updateYearDisplay = () => {
                const startYear = parseInt(yearStart.value);
                const endYear = parseInt(yearEnd.value);
                
                // Ensure start year is not greater than end year
                if (startYear > endYear) {
                    yearStart.value = endYear;
                }
                if (endYear < startYear) {
                    yearEnd.value = startYear;
                }
                
                yearDisplay.textContent = `${yearStart.value} - ${yearEnd.value}`;
            };

            yearStart.addEventListener('input', updateYearDisplay);
            yearEnd.addEventListener('input', updateYearDisplay);
            
            // Initialize display
            updateYearDisplay();
        }

        // Tactical dashboard year range sliders
        const tacticalYearStart = document.getElementById('tactical-year-start');
        const tacticalYearEnd = document.getElementById('tactical-year-end');
        const tacticalYearDisplay = document.getElementById('tactical-year-range-display');

        if (tacticalYearStart && tacticalYearEnd && tacticalYearDisplay) {
            const updateTacticalYearDisplay = () => {
                const startYear = parseInt(tacticalYearStart.value);
                const endYear = parseInt(tacticalYearEnd.value);
                
                // Ensure start year is not greater than end year
                if (startYear > endYear) {
                    tacticalYearStart.value = endYear;
                }
                if (endYear < startYear) {
                    tacticalYearEnd.value = startYear;
                }
                
                tacticalYearDisplay.textContent = `${tacticalYearStart.value} - ${tacticalYearEnd.value}`;
            };

            tacticalYearStart.addEventListener('input', updateTacticalYearDisplay);
            tacticalYearEnd.addEventListener('input', updateTacticalYearDisplay);
            
            // Initialize display
            updateTacticalYearDisplay();
        }

        // Lifecycle dashboard range sliders
        const lifecycleRating = document.getElementById('lifecycle-min-rating');
        const lifecycleRatingDisplay = document.getElementById('lifecycle-rating-display');
        const lifecycleVotes = document.getElementById('lifecycle-min-votes');
        const lifecycleVotesDisplay = document.getElementById('lifecycle-votes-display');

        if (lifecycleRating && lifecycleRatingDisplay) {
            const updateRatingDisplay = () => {
                lifecycleRatingDisplay.textContent = parseFloat(lifecycleRating.value).toFixed(1);
            };
            lifecycleRating.addEventListener('input', updateRatingDisplay);
            updateRatingDisplay();
        }

        if (lifecycleVotes && lifecycleVotesDisplay) {
            const updateVotesDisplay = () => {
                lifecycleVotesDisplay.textContent = parseInt(lifecycleVotes.value).toLocaleString();
            };
            lifecycleVotes.addEventListener('input', updateVotesDisplay);
            updateVotesDisplay();
        }
    }

    handleTabSwitch(tabName) {
        // Update active tab
        this.activeTab = tabName;
        
        // Update URL with tab parameter
        const url = new URL(window.location);
        url.searchParams.set('tab', tabName);
        window.history.pushState({}, '', url);
        
        // Show appropriate filter section (Bootstrap handles tab content)
        this.showFilterSection(tabName);
    }

    activateTab(tabName) {
        // Programmatically activate a tab using Bootstrap
        const tabElement = document.querySelector(`[data-tab="${tabName}"]`);
        if (tabElement) {
            const tab = new bootstrap.Tab(tabElement);
            tab.show();
        }
        
        // Update our internal state
        this.handleTabSwitch(tabName);
    }

    showFilterSection(tabName) {
        // Hide all filter sections
        document.querySelectorAll('[id$="-filters"]').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show appropriate filter section
        const filterSection = document.getElementById(`${tabName}-filters`);
        if (filterSection) {
            filterSection.style.display = 'block';
        }
    }

    handleFilterSubmit(event) {
        // Add loading state
        const submitButton = event.target.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Applying...';
        }
        
        // Form will submit normally, no need to prevent default
    }

    resetFilters(dashboardType) {
        const form = document.getElementById(`${dashboardType}-filter-form`);
        if (form) {
            // Reset form fields
            form.reset();
            
            // Reset range sliders to default values
            const rangeInputs = form.querySelectorAll('input[type="range"]');
            rangeInputs.forEach(input => {
                if (input.id.includes('year-start')) {
                    input.value = input.min;
                } else if (input.id.includes('year-end')) {
                    input.value = input.max;
                } else {
                    input.value = input.min;
                }
                input.dispatchEvent(new Event('input'));
            });
            
            // Reset multi-select fields
            const multiSelects = form.querySelectorAll('select[multiple]');
            multiSelects.forEach(select => {
                Array.from(select.options).forEach(option => {
                    option.selected = false;
                });
            });
            
            // Submit the reset form
            form.submit();
        }
    }
}

// Enhanced Filter Management
class FilterManager {
    constructor() {
        this.initializeQuickSelections();
    }

    initializeQuickSelections() {
        // Operational dashboard quick selections
        window.selectRecentYears = () => {
            const currentYear = new Date().getFullYear();
            const yearCheckboxes = document.querySelectorAll('input[name="op_years"]');
            yearCheckboxes.forEach(checkbox => {
                const year = parseInt(checkbox.value);
                checkbox.checked = year >= (currentYear - 5);
            });
        };

        window.selectAllMonths = () => {
            const monthCheckboxes = document.querySelectorAll('input[name="op_months"]');
            monthCheckboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
        };

        window.clearAllSelections = (type) => {
            const checkboxes = document.querySelectorAll(`input[name="${type}"]`);
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
        };
    }
}

// Initialize dashboard management when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing enhanced dashboard management...');
    
    // Initialize managers
    window.dashboardManager = new DashboardManager();
    window.filterManager = new FilterManager();
    
    // Set initial active tab based on URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const activeTab = urlParams.get('tab') || 'studio';
    
    // Wait a bit for Bootstrap to be ready, then activate the tab
    setTimeout(() => {
        window.dashboardManager.activateTab(activeTab);
    }, 100);
    
    console.log('Dashboard management initialized successfully');
});

// Utility functions for chart generation
function generateColors(count) {
    const colors = [
        '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', 
        '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43',
        '#ee5a24', '#0abde3', '#10ac84', '#f368e0', '#3742fa'
    ];
    
    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
} 