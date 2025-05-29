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

// Tab Management
class TabManager {
    constructor() {
        this.filterSections = {
            'studio-tab': 'studio-filters',
            'operational-tab': 'operational-filters',
            'tactical-tab': 'tactical-filters',
            'analytical-lifecycle-tab': 'lifecycle-filters',
            'analytical-evolution-tab': 'evolution-filters'
        };
        
        this.tabParamToId = {
            'studio': 'studio-tab',
            'operational': 'operational-tab',
            'tactical': 'tactical-tab',
            'analytical-lifecycle': 'analytical-lifecycle-tab',
            'analytical-evolution': 'analytical-evolution-tab'
        };
        
        this.init();
    }
    
    init() {
        this.setupTabSwitching();
        this.activateCorrectTab();
    }
    
    showFilterSection(tabId) {
        // Hide all filter sections
        Object.values(this.filterSections).forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.style.display = 'none';
            }
        });
        
        // Show relevant filter section
        if (this.filterSections[tabId]) {
            const section = document.getElementById(this.filterSections[tabId]);
            if (section) {
                section.style.display = 'block';
            }
        }
    }
    
    activateCorrectTab() {
        const urlParams = new URLSearchParams(window.location.search);
        const activeTabParam = urlParams.get('tab');
        
        if (activeTabParam && this.tabParamToId[activeTabParam]) {
            const targetTabId = this.tabParamToId[activeTabParam];
            const targetTab = document.getElementById(targetTabId);
            const targetPane = document.querySelector(targetTab.getAttribute('data-bs-target'));
            
            // Deactivate all tabs and panes
            document.querySelectorAll('[data-bs-toggle="tab"]').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            // Activate the target tab and pane
            targetTab.classList.add('active');
            if (targetPane) {
                targetPane.classList.add('show', 'active');
            }
            
            this.showFilterSection(targetTabId);
        } else {
            const studioTab = document.getElementById('studio-tab');
            if (studioTab) {
                this.showFilterSection('studio-tab');
            }
        }
    }
    
    setupTabSwitching() {
        const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = e.target.id;
                this.showFilterSection(tabId);
                
                // Update URL without reloading the page
                const tabParam = Object.keys(this.tabParamToId).find(key => this.tabParamToId[key] === tabId);
                if (tabParam) {
                    const newUrl = new URL(window.location);
                    newUrl.searchParams.set('tab', tabParam);
                    // Remove other tab-specific parameters to avoid conflicts
                    this.clearTabSpecificParams(newUrl);
                    window.history.replaceState({}, '', newUrl);
                }
                
                console.log(`Switched to tab: ${tabId}`);
            });
        });
    }
    
    clearTabSpecificParams(url) {
        const paramsToRemove = [
            'op_years', 'op_months', 'op_min_rating', 'op_timeframe',
            'tactical_platforms', 'tactical_genres', 'tactical_year_start', 'tactical_year_end',
            'lifecycle_genres', 'lifecycle_platforms', 'min_rating', 'min_votes',
            'evolution_genres', 'evolution_platforms'
        ];
        
        paramsToRemove.forEach(param => url.searchParams.delete(param));
    }
}

// Filter Management
class FilterManager {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupRangeSliders();
        this.setupResetButtons();
        this.setupQuickSelections();
    }
    
    setupRangeSliders() {
        // Year range sliders
        const yearStartSlider = document.getElementById('year-start');
        const yearEndSlider = document.getElementById('year-end');
        const yearRangeDisplay = document.getElementById('year-range-display');
        
        if (yearStartSlider && yearEndSlider && yearRangeDisplay) {
            const updateYearRange = () => {
                yearRangeDisplay.textContent = `${yearStartSlider.value} - ${yearEndSlider.value}`;
            };
            yearStartSlider.addEventListener('input', updateYearRange);
            yearEndSlider.addEventListener('input', updateYearRange);
        }
        
        // Tactical year range
        const tacticalYearStart = document.getElementById('tactical-year-start');
        const tacticalYearEnd = document.getElementById('tactical-year-end');
        const tacticalDisplay = document.getElementById('tactical-year-range-display');
        
        if (tacticalYearStart && tacticalYearEnd && tacticalDisplay) {
            const updateTacticalRange = () => {
                tacticalDisplay.textContent = `${tacticalYearStart.value} - ${tacticalYearEnd.value}`;
            };
            tacticalYearStart.addEventListener('input', updateTacticalRange);
            tacticalYearEnd.addEventListener('input', updateTacticalRange);
            updateTacticalRange(); // Initialize
        }
        
        // Lifecycle sliders
        const lifecycleRating = document.getElementById('lifecycle-min-rating');
        const lifecycleRatingDisplay = document.getElementById('lifecycle-rating-display');
        
        if (lifecycleRating && lifecycleRatingDisplay) {
            const updateRating = () => {
                lifecycleRatingDisplay.textContent = lifecycleRating.value;
            };
            lifecycleRating.addEventListener('input', updateRating);
            updateRating(); // Initialize
        }
        
        const lifecycleVotes = document.getElementById('lifecycle-min-votes');
        const lifecycleVotesDisplay = document.getElementById('lifecycle-votes-display');
        
        if (lifecycleVotes && lifecycleVotesDisplay) {
            const updateVotes = () => {
                lifecycleVotesDisplay.textContent = parseInt(lifecycleVotes.value).toLocaleString();
            };
            lifecycleVotes.addEventListener('input', updateVotes);
            updateVotes(); // Initialize
        }
    }
    
    setupResetButtons() {
        const resetButtons = [
            { id: 'reset-op-filters', url: '/?tab=operational' },
            { id: 'reset-tactical-filters', url: '/?tab=tactical' },
            { id: 'reset-lifecycle-filters', url: '/?tab=analytical-lifecycle' },
            { id: 'reset-evolution-filters', url: '/?tab=analytical-evolution' }
        ];
        
        resetButtons.forEach(({ id, url }) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', () => {
                    window.location.href = url;
                });
            }
        });
    }
    
    setupQuickSelections() {
        // Operational quick selections
        window.selectRecentYears = () => {
            const yearFilter = document.getElementById('op-year-filter');
            const currentYear = new Date().getFullYear();
            for (let i = 0; i < yearFilter.options.length; i++) {
                const year = parseInt(yearFilter.options[i].value);
                yearFilter.options[i].selected = year >= currentYear - 2;
            }
        };
        
        window.selectDecadeYears = () => {
            const yearFilter = document.getElementById('op-year-filter');
            const currentYear = new Date().getFullYear();
            for (let i = 0; i < yearFilter.options.length; i++) {
                const year = parseInt(yearFilter.options[i].value);
                yearFilter.options[i].selected = year >= currentYear - 9;
            }
        };
        
        window.clearYearSelection = () => {
            const yearFilter = document.getElementById('op-year-filter');
            for (let i = 0; i < yearFilter.options.length; i++) {
                yearFilter.options[i].selected = false;
            }
        };
        
        // Tactical quick selections
        window.selectMajorPlatforms = () => {
            const platformFilter = document.getElementById('tactical-platform-filter');
            const majorPlatforms = ['PlayStation', 'Xbox', 'Nintendo Switch', 'PC', 'PlayStation 4', 'Xbox One', 'PlayStation 5', 'Xbox Series X'];
            for (let i = 0; i < platformFilter.options.length; i++) {
                const option = platformFilter.options[i];
                option.selected = majorPlatforms.some(major => option.value.includes(major));
            }
        };
        
        window.clearPlatformSelection = () => {
            const platformFilter = document.getElementById('tactical-platform-filter');
            for (let i = 0; i < platformFilter.options.length; i++) {
                platformFilter.options[i].selected = false;
            }
        };
        
        window.selectPopularGenres = () => {
            const genreFilter = document.getElementById('tactical-genre-filter');
            const popularGenres = ['Action', 'Adventure', 'RPG', 'Strategy', 'Sports', 'Racing'];
            for (let i = 0; i < genreFilter.options.length; i++) {
                const option = genreFilter.options[i];
                option.selected = popularGenres.includes(option.value);
            }
        };
        
        window.clearGenreSelection = () => {
            const genreFilter = document.getElementById('tactical-genre-filter');
            for (let i = 0; i < genreFilter.options.length; i++) {
                genreFilter.options[i].selected = false;
            }
        };
        
        // Evolution quick selections
        window.selectEvolutionGenres = () => {
            const genreFilter = document.getElementById('evolution-genre-filter');
            const coreGenres = ['Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 'Puzzle'];
            for (let i = 0; i < genreFilter.options.length; i++) {
                const option = genreFilter.options[i];
                option.selected = coreGenres.includes(option.value);
            }
        };
        
        window.clearEvolutionGenres = () => {
            const genreFilter = document.getElementById('evolution-genre-filter');
            for (let i = 0; i < genreFilter.options.length; i++) {
                genreFilter.options[i].selected = false;
            }
        };
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize managers
    new TabManager();
    new FilterManager();
    
    // Initialize charts after data is loaded
    if (typeof initializeCharts === 'function') {
        initializeCharts();
    }
    
    console.log('Dashboard initialized successfully');
}); 