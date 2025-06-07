// Gaming Analytics Dashboard JavaScript

// Global variables for chart data (will be populated from server)
let stats, topGames, platformCounts, genreCounts, gamesPerYear, publisherCounts;
let avgRatingPlatform, avgRatingDeveloper, directorAnalytics, gameTypeDistribution;
let ratingDistribution, votesAnalytics, mostVotedGames, collectionSummary;
let recentReleases, ratingTrends, monthlyActivity, platformPerformance, topRatedRecent;
let tacticalSankeyData, tacticalVennData, tacticalChordData, tacticalDumbbellData, tacticalMarimekkoData;
let lifecycleSurvivalData, lifecycleRidgelineData, lifecycleTimelineData, lifecycleHexbinData, lifecycleParallelData;
let evolutionStreamData, evolutionBubbleData, evolutionHexbinData, evolutionParallelData, evolutionTreeData;
let tacticalDeveloperProfiles;

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

        // Setup "All" option handlers for tactical filters
        this.setupTacticalAllOptionHandlers();

        // Platform and genre quick selection buttons
        this.setupQuickSelectionButtons();
    }

    setupTacticalAllOptionHandlers() {
        // Studio Type "All" handler
        const studioTypeSelect = document.getElementById('tactical-studio-type');
        if (studioTypeSelect) {
            studioTypeSelect.addEventListener('change', (e) => {
                this.handleAllOptionSelection(e.target, 'all_studios');
            });
        }

        // Country "All" handler
        const countrySelect = document.getElementById('tactical-country-filter');
        if (countrySelect) {
            countrySelect.addEventListener('change', (e) => {
                this.handleAllOptionSelection(e.target, 'all_countries');
            });
        }

        // Maturity "All" handler
        const maturitySelect = document.getElementById('tactical-maturity-filter');
        if (maturitySelect) {
            maturitySelect.addEventListener('change', (e) => {
                this.handleAllOptionSelection(e.target, 'all_maturity');
            });
        }
    }

    handleAllOptionSelection(selectElement, allOptionValue) {
        const allOption = Array.from(selectElement.options).find(option => option.value === allOptionValue);
        const otherOptions = Array.from(selectElement.options).filter(option => option.value !== allOptionValue);
        
        if (allOption && allOption.selected) {
            // If "All" is selected, deselect all other options
            otherOptions.forEach(option => {
                option.selected = false;
            });
        } else {
            // If any other option is selected, deselect "All"
            const hasOtherSelected = otherOptions.some(option => option.selected);
            if (hasOtherSelected && allOption) {
                allOption.selected = false;
            }
            
            // If no options are selected, select "All" by default
            const hasAnySelected = Array.from(selectElement.options).some(option => option.selected);
            if (!hasAnySelected && allOption) {
                allOption.selected = true;
            }
        }
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

        // Tactical Dashboard Quick Selection Functions
        window.selectMajorStudios = () => {
            const studioSelect = document.getElementById('tactical-studio-type');
            if (studioSelect) {
                const majorStudios = ['AAA', 'Mid-tier'];
                Array.from(studioSelect.options).forEach(option => {
                    option.selected = majorStudios.includes(option.value);
                });
            }
        };

        window.selectAllStudios = () => {
            const studioSelect = document.getElementById('tactical-studio-type');
            if (studioSelect) {
                Array.from(studioSelect.options).forEach(option => {
                    option.selected = option.value === 'all_studios';
                });
            }
        };

        window.selectTopCountries = () => {
            const countrySelect = document.getElementById('tactical-country-filter');
            if (countrySelect) {
                const topCountries = ['United States', 'Japan', 'United Kingdom', 'Canada', 'Germany'];
                Array.from(countrySelect.options).forEach(option => {
                    option.selected = topCountries.includes(option.value);
                });
            }
        };

        window.selectAllCountries = () => {
            const countrySelect = document.getElementById('tactical-country-filter');
            if (countrySelect) {
                Array.from(countrySelect.options).forEach(option => {
                    option.selected = option.value === 'all_countries';
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
        console.log(`Resetting filters for ${dashboardType} dashboard`);
        
        switch(dashboardType) {
            case 'studio':
                // Reset studio performance filters
                const genreFilter = document.getElementById('genre-filter');
                const platformFilter = document.getElementById('platform-filter');
                const yearStart = document.getElementById('year-start');
                const yearEnd = document.getElementById('year-end');
                
                if (genreFilter) genreFilter.selectedIndex = -1;
                if (platformFilter) platformFilter.selectedIndex = -1;
                if (yearStart) yearStart.value = yearStart.min;
                if (yearEnd) yearEnd.value = yearEnd.max;
                break;
                
            case 'op':
            case 'operational':
                // Reset operational dashboard filters
                const opYearFilter = document.getElementById('op-year-filter');
                const opMonthFilter = document.getElementById('op-month-filter');
                const opRatingFilter = document.getElementById('op-rating-filter');
                const opTimeframe = document.getElementById('op-timeframe');
                
                if (opYearFilter) opYearFilter.selectedIndex = -1;
                if (opMonthFilter) opMonthFilter.selectedIndex = -1;
                if (opRatingFilter) opRatingFilter.selectedIndex = 0;
                if (opTimeframe) opTimeframe.selectedIndex = 1; // Default to 'recent'
                break;
                
            case 'tactical':
                // Reset tactical dashboard filters
                const tacticalStudioType = document.getElementById('tactical-studio-type');
                const tacticalCountryFilter = document.getElementById('tactical-country-filter');
                const tacticalMaturityFilter = document.getElementById('tactical-maturity-filter');
                const tacticalAnalysisType = document.getElementById('tactical-analysis-type');
                const tacticalYearStart = document.getElementById('tactical-year-start');
                const tacticalYearEnd = document.getElementById('tactical-year-end');
                
                // Reset to "All" options
                if (tacticalStudioType) {
                    Array.from(tacticalStudioType.options).forEach(option => {
                        option.selected = option.value === 'all_studios';
                    });
                }
                
                if (tacticalCountryFilter) {
                    Array.from(tacticalCountryFilter.options).forEach(option => {
                        option.selected = option.value === 'all_countries';
                    });
                }
                
                if (tacticalMaturityFilter) {
                    Array.from(tacticalMaturityFilter.options).forEach(option => {
                        option.selected = option.value === 'all_maturity';
                    });
                }
                
                if (tacticalAnalysisType) tacticalAnalysisType.selectedIndex = 0;
                if (tacticalYearStart) tacticalYearStart.value = tacticalYearStart.min;
                if (tacticalYearEnd) tacticalYearEnd.value = tacticalYearEnd.max;
                
                // Update year range display
                const tacticalYearDisplay = document.getElementById('tactical-year-range-display');
                if (tacticalYearDisplay && tacticalYearStart && tacticalYearEnd) {
                    tacticalYearDisplay.textContent = `${tacticalYearStart.value} - ${tacticalYearEnd.value}`;
                }
                break;
                
            case 'lifecycle':
                // Reset lifecycle dashboard filters
                const lifecycleSearch = document.getElementById('lifecycle-search');
                const lifecycleGenreFilter = document.getElementById('lifecycle-genre-filter');
                const lifecyclePlatformFilter = document.getElementById('lifecycle-platform-filter');
                const lifecycleMinRating = document.getElementById('lifecycle-min-rating');
                const lifecycleMinVotes = document.getElementById('lifecycle-min-votes');
                const lifecycleGameType = document.getElementById('lifecycle-game-type');
                
                if (lifecycleSearch) lifecycleSearch.value = '';
                if (lifecycleGenreFilter) lifecycleGenreFilter.selectedIndex = -1;
                if (lifecyclePlatformFilter) lifecyclePlatformFilter.selectedIndex = -1;
                if (lifecycleMinRating) lifecycleMinRating.value = '0.0';
                if (lifecycleMinVotes) lifecycleMinVotes.value = '0';
                if (lifecycleGameType) lifecycleGameType.selectedIndex = 0;
                
                // Update range displays
                const lifecycleRatingDisplay = document.getElementById('lifecycle-rating-display');
                const lifecycleVotesDisplay = document.getElementById('lifecycle-votes-display');
                if (lifecycleRatingDisplay) lifecycleRatingDisplay.textContent = '0.0';
                if (lifecycleVotesDisplay) lifecycleVotesDisplay.textContent = '0';
                break;
                
            case 'evolution':
                // Reset evolution dashboard filters
                const evolutionGenreFilter = document.getElementById('evolution-genre-filter');
                const evolutionPlatformFilter = document.getElementById('evolution-platform-filter');
                const evolutionTimePeriod = document.getElementById('evolution-time-period');
                const evolutionMetric = document.getElementById('evolution-metric');
                
                if (evolutionGenreFilter) evolutionGenreFilter.selectedIndex = -1;
                if (evolutionPlatformFilter) evolutionPlatformFilter.selectedIndex = -1;
                if (evolutionTimePeriod) evolutionTimePeriod.selectedIndex = 0;
                if (evolutionMetric) evolutionMetric.selectedIndex = 0;
                break;
        }
        
        // Auto-submit the form after reset
        const form = document.getElementById(`${dashboardType}-filter-form`);
        if (form) {
            setTimeout(() => {
                form.submit();
            }, 100);
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