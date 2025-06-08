// Advanced Charts for Tactical, Lifecycle, and Evolution Dashboards

// Enhanced Developer Performance Dashboard Charts
function initializeTacticalCharts() {
    console.log('Initializing enhanced tactical charts...');
    
    // Assign data to window variables for chart functions
    if (typeof tacticalSankeyData !== 'undefined') window.tacticalSankeyData = tacticalSankeyData;
    if (typeof tacticalVennData !== 'undefined') window.tacticalVennData = tacticalVennData;
    if (typeof tacticalChordData !== 'undefined') window.tacticalChordData = tacticalChordData;
    if (typeof tacticalDumbbellData !== 'undefined') window.tacticalDumbbellData = tacticalDumbbellData;
    if (typeof tacticalMarimekkoData !== 'undefined') window.tacticalMarimekkoData = tacticalMarimekkoData;
    if (typeof tacticalDeveloperProfiles !== 'undefined') window.tacticalDeveloperProfiles = tacticalDeveloperProfiles;
    
    // Initialize all tactical charts
    initializeDeveloperMaturityGroupedBar();
    initializeDeveloperReplayRateGroupedMinMaxAvg();
    initializeDeveloperGeographicDualAxis();
    initializeTopGamesByCountryChart();
    initializeDeveloperCountryStudioHeatmap();
    initializeDeveloperPerformanceHorizontalGrouped();
    initializeDeveloperProfileTable();
}

// Helper function to get consistent colors for studio types
function getStudioTypeColor(studioType) {
    const colorMap = {
        'AAA': 'rgba(233, 69, 96, 0.8)',        // Red
        'Mid-tier': 'rgba(54, 162, 235, 0.8)',  // Blue
        'Indie': 'rgba(255, 206, 86, 0.8)',     // Yellow
        'Mobile': 'rgba(75, 192, 192, 0.8)',    // Teal
        'Legacy': 'rgba(153, 102, 255, 0.8)',   // Purple
        'Specialized': 'rgba(255, 159, 64, 0.8)' // Orange
    };
    
    return colorMap[studioType] || 'rgba(201, 203, 207, 0.8)'; // Default gray
}

// Helper function for maturity colors
function getMaturityColor(level) {
    const colors = {
        'Veteran': '#e74c3c',
        'Established': '#f39c12',
        'Emerging': '#3498db',
        'Developing': '#2ecc71'
    };
    return colors[level] || '#95a5a6';
}

// 1. 🎯 Developer Maturity vs Performance - Grouped Vertical Bar Chart
function initializeDeveloperMaturityGroupedBar() {
    try {
        console.log('Initializing Developer Maturity Grouped Bar Chart');
        
        const ctx = document.getElementById('tacticalChart4');
        if (!ctx) {
            console.warn('Chart canvas tacticalChart4 not found');
            return;
        }

        // Create sample data if no real data available
        let chartData = [];
        if (window.tacticalDumbbellData && Array.isArray(window.tacticalDumbbellData)) {
            chartData = window.tacticalDumbbellData;
        } else {
            // Sample data for demonstration
            chartData = [
                { studio_type: 'AAA', maturity_level: 'Veteran', replay_rate: 0.85 },
                { studio_type: 'AAA', maturity_level: 'Established', replay_rate: 0.78 },
                { studio_type: 'Mid-tier', maturity_level: 'Established', replay_rate: 0.72 },
                { studio_type: 'Mid-tier', maturity_level: 'Emerging', replay_rate: 0.65 },
                { studio_type: 'Indie', maturity_level: 'Emerging', replay_rate: 0.58 },
                { studio_type: 'Mobile', maturity_level: 'Emerging', replay_rate: 0.55 }
            ];
        }

        // Process data for grouped bar chart
        const maturityLevels = ['Emerging', 'Developing', 'Established', 'Veteran'];
        const studioTypes = [...new Set(chartData.map(d => d.studio_type))];
        
        const datasets = studioTypes.map((studioType, index) => {
            const data = maturityLevels.map(maturity => {
                const item = chartData.find(d => 
                    d.maturity_level === maturity && d.studio_type === studioType
                );
                return item ? item.replay_rate : 0;
            });
            
            return {
                label: studioType,
                data: data,
                backgroundColor: getStudioTypeColor(studioType),
                borderColor: getStudioTypeColor(studioType),
                borderWidth: 1,
                borderRadius: 4
            };
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: maturityLevels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '🎯 Developer Maturity vs Performance',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Maturity Level'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Average Replay Rate'
                        },
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return (value * 100).toFixed(0) + '%';
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        console.log('Developer Maturity Grouped Bar Chart initialized successfully');
    } catch (error) {
        console.error('Error initializing Developer Maturity Grouped Bar Chart:', error);
    }
}

// 2. 🧪 Replay Rate Distribution by Studio Type - Grouped Bar Chart (Min, Avg, Max)
function initializeDeveloperReplayRateGroupedMinMaxAvg() {
    try {
        console.log('Initializing Developer Replay Rate Min/Max/Avg Chart');
        
        const ctx = document.getElementById('tacticalChart5');
        if (!ctx) {
            console.warn('Chart canvas tacticalChart5 not found');
            return;
        }

        // Create sample data if no real data available
        let chartData = [];
        if (window.tacticalSankeyData && Array.isArray(window.tacticalSankeyData)) {
            chartData = window.tacticalSankeyData;
        } else {
            // Sample data for demonstration
            chartData = [
                { studio_type: 'AAA', avg_replay_rate: 0.75, min_replay_rate: 0.65, max_replay_rate: 0.85, total_developers: 150 },
                { studio_type: 'Mid-tier', avg_replay_rate: 0.68, min_replay_rate: 0.58, max_replay_rate: 0.78, total_developers: 85 },
                { studio_type: 'Indie', avg_replay_rate: 0.62, min_replay_rate: 0.52, max_replay_rate: 0.72, total_developers: 45 },
                { studio_type: 'Mobile', avg_replay_rate: 0.58, min_replay_rate: 0.48, max_replay_rate: 0.68, total_developers: 30 }
            ];
        }

        const studioTypes = chartData.map(d => d.studio_type);
        const minRates = chartData.map(d => d.min_replay_rate || d.avg_replay_rate * 0.8);
        const avgRates = chartData.map(d => d.avg_replay_rate);
        const maxRates = chartData.map(d => d.max_replay_rate || d.avg_replay_rate * 1.2);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: studioTypes,
                datasets: [
                    {
                        label: 'Minimum',
                        data: minRates,
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        borderRadius: 4
                    },
                    {
                        label: 'Average',
                        data: avgRates,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        borderRadius: 4
                    },
                    {
                        label: 'Maximum',
                        data: maxRates,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '🧪 Replay Rate Distribution by Studio Type',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            afterBody: function(context) {
                                const index = context[0].dataIndex;
                                const studioData = chartData[index];
                                return `Developer Count: ${studioData.total_developers || 'N/A'}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Studio Type'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Replay Rate'
                        },
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return (value * 100).toFixed(0) + '%';
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        console.log('Developer Replay Rate Min/Max/Avg Chart initialized successfully');
    } catch (error) {
        console.error('Error initializing Developer Replay Rate Min/Max/Avg Chart:', error);
    }
}

// 3. 🌍 Developer Geographic Distribution - Dual Y-Axis Chart (Bar + Line)
function initializeDeveloperGeographicDualAxis() {
    try {
        console.log('Initializing Developer Geographic Dual Axis Chart');
        
        const ctx = document.getElementById('tacticalChart2');
        if (!ctx) {
            console.warn('Chart canvas tacticalChart2 not found');
            return;
        }

        // Create sample data if no real data available
        let chartData = [];
        if (window.tacticalVennData && Array.isArray(window.tacticalVennData)) {
            chartData = window.tacticalVennData;
        } else {
            // Sample data for demonstration
            chartData = [
                { country: 'United States', total_developers: 850, avg_replay_rate: 0.72 },
                { country: 'Japan', total_developers: 320, avg_replay_rate: 0.78 },
                { country: 'United Kingdom', total_developers: 280, avg_replay_rate: 0.69 },
                { country: 'Canada', total_developers: 240, avg_replay_rate: 0.71 },
                { country: 'Germany', total_developers: 180, avg_replay_rate: 0.68 },
                { country: 'France', total_developers: 160, avg_replay_rate: 0.75 }
            ];
        }

        // Get top games data for tooltips
        let topGamesData = {};
        if (window.tacticalChordData && Array.isArray(window.tacticalChordData)) {
            window.tacticalChordData.forEach(countryData => {
                if (countryData.country && countryData.top_games) {
                    topGamesData[countryData.country] = countryData.top_games.slice(0, 3);
                }
            });
        }

        // Sort countries by developer count for better visualization
        const sortedData = chartData
            .filter(d => d.total_developers > 0)
            .sort((a, b) => b.total_developers - a.total_developers)
            .slice(0, 10);

        const countries = sortedData.map(d => d.country);
        const developerCounts = sortedData.map(d => d.total_developers);
        const avgReplayRates = sortedData.map(d => d.avg_replay_rate);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: countries,
                datasets: [
                    {
                        label: 'Developer Count',
                        data: developerCounts,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        yAxisID: 'y',
                        borderRadius: 4
                    },
                    {
                        label: 'Avg Replay Rate',
                        data: avgReplayRates,
                        type: 'line',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderWidth: 3,
                        fill: false,
                        yAxisID: 'y1',
                        tension: 0.4,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '🌍 Developer Geographic Distribution',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            afterBody: function(context) {
                                const countryIndex = context[0].dataIndex;
                                const country = countries[countryIndex];
                                const topGames = topGamesData[country];
                                
                                if (topGames && topGames.length > 0) {
                                    let gamesList = '\n🎮 Top Games:';
                                    topGames.forEach((game, index) => {
                                        gamesList += `\n${index + 1}. ${game.title} (${game.rating}/10)`;
                                        if (game.developer) {
                                            gamesList += ` - ${game.developer}`;
                                        }
                                    });
                                    return gamesList;
                                }
                                return '';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Country'
                        },
                        ticks: {
                            maxRotation: 45
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Developer Count'
                        },
                        beginAtZero: true
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Average Replay Rate'
                        },
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false
                        },
                        ticks: {
                            callback: function(value) {
                                return (value * 100).toFixed(0) + '%';
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        console.log('Developer Geographic Dual Axis Chart initialized successfully');
    } catch (error) {
        console.error('Error initializing Developer Geographic Dual Axis Chart:', error);
    }
}

// 4. 🧱 Country × Studio Type Matrix - Heatmap Grid
function initializeDeveloperCountryStudioHeatmap() {
    try {
        console.log('Initializing Enhanced Country × Studio Type Matrix');
        
        const canvas = document.getElementById('tacticalChart6');
        if (!canvas) {
            console.warn('Canvas tacticalChart6 not found');
            return;
        }

        // Get data from global variable
        const rawData = window.tacticalMatrixData || [];
        
        console.log('=== HEATMAP DEBUG ===');
        console.log('Raw matrix data:', rawData);
        console.log('Data length:', rawData.length);
        console.log('Data type:', typeof rawData);
        console.log('Is array:', Array.isArray(rawData));
        
        if (!rawData || rawData.length === 0) {
            console.warn('No matrix data available, showing error message');
            const ctx = canvas.getContext('2d');
            
            // Clear canvas and show error message
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ff6b6b';
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No country-studio data available', canvas.width / 2, canvas.height / 2 - 20);
            ctx.fillStyle = '#ffa726';
            ctx.font = '14px Arial';
            ctx.fillText('Check data source and filters', canvas.width / 2, canvas.height / 2 + 10);
            return;
        }

        console.log('Sample data points:', rawData.slice(0, 3));

        // Process data for different chart types
        const countries = [...new Set(rawData.map(d => d.country))].sort();
        const studioTypes = [...new Set(rawData.map(d => d.studio_type))].sort();
        
        console.log('Extracted countries:', countries);
        console.log('Extracted studio types:', studioTypes);
        
        // Create data lookup
        const dataLookup = {};
        rawData.forEach(d => {
            const key = `${d.country}-${d.studio_type}`;
            dataLookup[key] = d.developer_count;
        });
        
        console.log('Data lookup sample:', Object.keys(dataLookup).slice(0, 5));

        // Function to render chart based on selected type
        function renderChart(visualizationType) {
            console.log('Rendering chart type:', visualizationType);
            
            // Destroy existing chart
            if (window.tacticalChart6Instance) {
                window.tacticalChart6Instance.destroy();
            }

            const ctx = canvas.getContext('2d');
            
            if (visualizationType === 'heatmap') {
                createHeatmapChart(ctx, canvas, countries, studioTypes, dataLookup, rawData);
                updateChartDescription('Color-encoded grid showing developer count by country and studio type');
            } else if (visualizationType === 'groupedBar') {
                createGroupedBarChart(ctx, canvas, countries, studioTypes, dataLookup, rawData);
                updateChartDescription('Horizontal bars comparing developer counts across countries by studio type');
            } else if (visualizationType === 'stackedColumn') {
                createStackedColumnChart(ctx, canvas, countries, studioTypes, dataLookup, rawData);
                updateChartDescription('Percentage distribution of studio types within each country');
            }
        }

        // Function to update chart description
        function updateChartDescription(description) {
            const descElement = document.getElementById('matrixChartDescription');
            if (descElement) {
                descElement.textContent = description;
            }
        }

        // Set up visualization type selector
        const selector = document.getElementById('matrixVisualizationType');
        if (selector) {
            selector.addEventListener('change', function() {
                renderChart(this.value);
            });
        }

        // Initial render with default type (heatmap)
        const initialType = selector ? selector.value : 'heatmap';
        console.log('Initial chart type:', initialType);
        renderChart(initialType);

    } catch (error) {
        console.error('Error in initializeDeveloperCountryStudioHeatmap:', error);
        console.error('Error stack:', error.stack);
    }
}

function createHeatmapChart(ctx, canvas, countries, studioTypes, dataLookup, rawData) {
    // 🔥 Enhanced Heatmap Implementation
    const maxCount = Math.max(...rawData.map(d => d.developer_count));
    const minCount = Math.min(...rawData.map(d => d.developer_count));
    
    console.log('=== HEATMAP CREATION DEBUG ===');
    console.log('Creating heatmap with:', { countries, studioTypes, maxCount, minCount });
    console.log('Raw data sample:', rawData.slice(0, 3));
    
    // Create heatmap data points
    const heatmapData = [];
    countries.forEach((country, countryIndex) => {
        studioTypes.forEach((studioType, studioIndex) => {
            const key = `${country}-${studioType}`;
            const count = dataLookup[key] || 0;
            const dataPoint = rawData.find(d => d.country === country && d.studio_type === studioType);
            
            heatmapData.push({
                x: studioIndex,
                y: countryIndex,
                v: count,
                country: country,
                studioType: studioType,
                replayRate: dataPoint ? dataPoint.avg_replay_rate : 0
            });
        });
    });
    
    console.log('Generated heatmap data points:', heatmapData.length);
    console.log('Sample heatmap points:', heatmapData.slice(0, 5));
    console.log('Non-zero points:', heatmapData.filter(p => p.v > 0).length);

    const config = {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Developer Count',
                data: heatmapData,
                backgroundColor: function(context) {
                    const value = context.parsed.v;
                    if (value === 0) return 'rgba(100, 100, 100, 0.3)';
                    const intensity = maxCount > 0 ? value / maxCount : 0;
                    // Use a more vibrant color scheme
                    const red = Math.floor(255 * intensity);
                    const blue = Math.floor(255 * (1 - intensity));
                    return `rgba(${red}, 100, ${blue}, 0.8)`;
                },
                borderColor: function(context) {
                    const value = context.parsed.v;
                    if (value === 0) return 'rgba(150, 150, 150, 0.5)';
                    const intensity = maxCount > 0 ? value / maxCount : 0;
                    const red = Math.floor(255 * intensity);
                    const blue = Math.floor(255 * (1 - intensity));
                    return `rgba(${red}, 100, ${blue}, 1)`;
                },
                borderWidth: 2,
                pointRadius: function(context) {
                    const value = context.parsed.v;
                    if (value === 0) return 8;
                    const intensity = maxCount > 0 ? value / maxCount : 0;
                    return Math.max(12, 12 + intensity * 20);
                },
                pointHoverRadius: function(context) {
                    const value = context.parsed.v;
                    if (value === 0) return 10;
                    const intensity = maxCount > 0 ? value / maxCount : 0;
                    return Math.max(15, 15 + intensity * 25);
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#444',
                    borderWidth: 1,
                    callbacks: {
                        title: function(context) {
                            const point = context[0];
                            return `${point.raw.country} × ${point.raw.studioType}`;
                        },
                        label: function(context) {
                            const point = context.raw;
                            const lines = [`Developers: ${point.v}`];
                            if (point.replayRate > 0) {
                                lines.push(`Replay Rate: ${(point.replayRate * 100).toFixed(1)}%`);
                            }
                            return lines;
                        },
                        afterBody: function(context) {
                            const point = context[0].raw;
                            if (point.v === 0) {
                                return 'No developers in this category';
                            }
                            const intensity = maxCount > 0 ? point.v / maxCount : 0;
                            if (intensity > 0.7) return '🔥 High concentration';
                            if (intensity > 0.4) return '📈 Medium concentration';
                            return '📊 Low concentration';
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    min: -0.5,
                    max: studioTypes.length - 0.5,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return studioTypes[Math.round(value)] || '';
                        },
                        color: '#eee',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Studio Type',
                        color: '#eee',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)',
                        lineWidth: 1
                    }
                },
                y: {
                    type: 'linear',
                    min: -0.5,
                    max: countries.length - 0.5,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            const country = countries[Math.round(value)];
                            return country && country.length > 12 ? country.substring(0, 12) + '...' : country || '';
                        },
                        color: '#eee',
                        font: {
                            size: 11,
                            weight: 'bold'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Country',
                        color: '#eee',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)',
                        lineWidth: 1
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'point'
            }
        }
    };

    console.log('Creating Chart.js instance with config:', config);
    window.tacticalChart6Instance = new Chart(ctx, config);
    console.log('Chart instance created:', window.tacticalChart6Instance);
}

function createGroupedBarChart(ctx, canvas, countries, studioTypes, dataLookup, rawData) {
    // 📊 Enhanced Grouped Horizontal Bar Chart Implementation
    console.log('Creating grouped bar chart with:', { countries, studioTypes });
    
    const datasets = studioTypes.map((studioType, index) => {
        const data = countries.map(country => {
            const key = `${country}-${studioType}`;
            return dataLookup[key] || 0;
        });
        
        return {
            label: studioType,
            data: data,
            backgroundColor: getStudioTypeColor(studioType),
            borderColor: getStudioTypeColor(studioType).replace('0.8', '1'),
            borderWidth: 2,
            borderRadius: 4,
            borderSkipped: false,
        };
    });

    const config = {
        type: 'bar',
        data: {
            labels: countries.map(country => 
                country.length > 15 ? country.substring(0, 15) + '...' : country
            ),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y', // Horizontal bars
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#eee',
                        font: {
                            size: 12,
                            weight: 'bold'
                        },
                        usePointStyle: true,
                        pointStyle: 'rect',
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#444',
                    borderWidth: 1,
                    callbacks: {
                        title: function(context) {
                            const fullCountryName = countries[context[0].dataIndex];
                            return fullCountryName;
                        },
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.x} developers`;
                        },
                        afterBody: function(context) {
                            const countryIndex = context[0].dataIndex;
                            const country = countries[countryIndex];
                            const totalDevs = studioTypes.reduce((sum, studioType) => {
                                const key = `${country}-${studioType}`;
                                return sum + (dataLookup[key] || 0);
                            }, 0);
                            return `Total developers in ${country}: ${totalDevs}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Developers',
                        color: '#eee',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        color: '#eee',
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)',
                        lineWidth: 1
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Country',
                        color: '#eee',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        color: '#eee',
                        font: {
                            size: 11,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        lineWidth: 1
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };

    window.tacticalChart6Instance = new Chart(ctx, config);
}

function createStackedColumnChart(ctx, canvas, countries, studioTypes, dataLookup, rawData) {
    // 🧩 Enhanced 100% Stacked Column Chart Implementation
    console.log('Creating stacked column chart with:', { countries, studioTypes });
    
    const datasets = studioTypes.map((studioType, index) => {
        const data = countries.map(country => {
            const key = `${country}-${studioType}`;
            const count = dataLookup[key] || 0;
            
            // Calculate total for this country
            const countryTotal = studioTypes.reduce((sum, st) => {
                const k = `${country}-${st}`;
                return sum + (dataLookup[k] || 0);
            }, 0);
            
            // Return percentage
            return countryTotal > 0 ? (count / countryTotal) * 100 : 0;
        });
        
        return {
            label: studioType,
            data: data,
            backgroundColor: getStudioTypeColor(studioType),
            borderColor: getStudioTypeColor(studioType).replace('0.8', '1'),
            borderWidth: 2,
            borderRadius: {
                topLeft: index === studioTypes.length - 1 ? 4 : 0,
                topRight: index === studioTypes.length - 1 ? 4 : 0,
                bottomLeft: index === 0 ? 4 : 0,
                bottomRight: index === 0 ? 4 : 0
            }
        };
    });

    const config = {
        type: 'bar',
        data: {
            labels: countries.map(country => 
                country.length > 12 ? country.substring(0, 12) + '...' : country
            ),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#eee',
                        font: {
                            size: 12,
                            weight: 'bold'
                        },
                        usePointStyle: true,
                        pointStyle: 'rect',
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#444',
                    borderWidth: 1,
                    callbacks: {
                        title: function(context) {
                            const fullCountryName = countries[context[0].dataIndex];
                            return fullCountryName;
                        },
                        label: function(context) {
                            const percentage = context.parsed.y.toFixed(1);
                            const countryIndex = context.dataIndex;
                            const country = countries[countryIndex];
                            const studioType = context.dataset.label;
                            const key = `${country}-${studioType}`;
                            const actualCount = dataLookup[key] || 0;
                            return `${studioType}: ${percentage}% (${actualCount} developers)`;
                        },
                        afterBody: function(context) {
                            const countryIndex = context[0].dataIndex;
                            const country = countries[countryIndex];
                            const totalDevs = studioTypes.reduce((sum, studioType) => {
                                const key = `${country}-${studioType}`;
                                return sum + (dataLookup[key] || 0);
                            }, 0);
                            return `Total developers: ${totalDevs}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Country',
                        color: '#eee',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        color: '#eee',
                        maxRotation: 45,
                        font: {
                            size: 10,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        lineWidth: 1
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage Distribution (%)',
                        color: '#eee',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        color: '#eee',
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)',
                        lineWidth: 1
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };

    window.tacticalChart6Instance = new Chart(ctx, config);
}

// 5. 📊 Developer Performance Metrics - Horizontal Grouped Bar Chart
function initializeDeveloperPerformanceHorizontalGrouped() {
    try {
        console.log('Initializing Developer Performance Horizontal Grouped Chart');
        
        const ctx = document.getElementById('tacticalChart1');
        if (!ctx) {
            console.warn('Chart canvas tacticalChart1 not found');
            return;
        }

        // Create sample data if no real data available
        let chartData = [];
        if (window.tacticalSankeyData && Array.isArray(window.tacticalSankeyData)) {
            chartData = window.tacticalSankeyData;
        } else {
            // Sample data for demonstration
            chartData = [
                { studio_type: 'AAA', avg_replay_rate: 0.75, avg_years_active: 25, market_presence: 8 },
                { studio_type: 'Mid-tier', avg_replay_rate: 0.68, avg_years_active: 18, market_presence: 6 },
                { studio_type: 'Indie', avg_replay_rate: 0.62, avg_years_active: 12, market_presence: 4 },
                { studio_type: 'Mobile', avg_replay_rate: 0.58, avg_years_active: 8, market_presence: 5 }
            ];
        }

        // Performance dimensions
        const dimensions = ['Retention Rate', 'Experience Level', 'Market Reach'];
        const studioTypes = chartData.map(d => d.studio_type);

        const datasets = studioTypes.map((studioType, index) => {
            const studioData = chartData[index];
            
            // Normalize metrics to 0-100 scale
            const retentionScore = (studioData.avg_replay_rate || 0) * 100;
            const experienceScore = Math.min(100, (studioData.avg_years_active || 0) * 4);
            const reachScore = Math.min(100, (studioData.market_presence || 1) * 12);
            
            return {
                label: studioType,
                data: [retentionScore, experienceScore, reachScore],
                backgroundColor: getStudioTypeColor(studioType),
                borderColor: getStudioTypeColor(studioType),
                borderWidth: 1,
                borderRadius: 4
            };
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dimensions,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    title: {
                        display: true,
                        text: '📊 Developer Performance Metrics',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Normalized Score (0-100)'
                        },
                        beginAtZero: true,
                        max: 100
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Performance Dimensions'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        console.log('Developer Performance Horizontal Grouped Chart initialized successfully');
    } catch (error) {
        console.error('Error initializing Developer Performance Horizontal Grouped Chart:', error);
    }
}

// 6. 🎮 Top Games by Country - Horizontal Bar Chart with Game Details
function initializeTopGamesByCountryChart() {
    try {
        console.log('Initializing Top Games by Country Chart');
        
        const ctx = document.getElementById('tacticalChart3');
        if (!ctx) {
            console.warn('Chart canvas tacticalChart3 not found');
            return;
        }

        // Get top games data
        let topGamesData = [];
        if (window.tacticalChordData && Array.isArray(window.tacticalChordData)) {
            // Flatten all top games from all countries
            window.tacticalChordData.forEach(countryData => {
                if (countryData.country && countryData.top_games) {
                    countryData.top_games.slice(0, 3).forEach(game => {
                        topGamesData.push({
                            ...game,
                            country: countryData.country
                        });
                    });
                }
            });
        } else {
            // Sample data for demonstration
            topGamesData = [
                { title: 'The Legend of Zelda: Breath of the Wild', rating: 9.3, country: 'Japan', developer: 'Nintendo EPD' },
                { title: 'Red Dead Redemption 2', rating: 9.1, country: 'United States', developer: 'Rockstar Games' },
                { title: 'God of War', rating: 9.0, country: 'United States', developer: 'Santa Monica Studio' },
                { title: 'Persona 5', rating: 8.9, country: 'Japan', developer: 'Atlus' },
                { title: 'Grand Theft Auto V', rating: 8.8, country: 'United Kingdom', developer: 'Rockstar North' },
                { title: 'The Witcher 3: Wild Hunt', rating: 8.7, country: 'Poland', developer: 'CD Projekt RED' }
            ];
        }

        // Sort by rating and take top 10
        const sortedGames = topGamesData
            .sort((a, b) => b.rating - a.rating)
            .slice(0, 10);

        const gameLabels = sortedGames.map(game => 
            game.title.length > 25 ? game.title.substring(0, 25) + '...' : game.title
        );
        const ratings = sortedGames.map(game => game.rating);
        const countries = sortedGames.map(game => game.country);

        // Create color mapping for countries
        const uniqueCountries = [...new Set(countries)];
        const countryColors = {};
        const colorPalette = [
            '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', 
            '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43'
        ];
        uniqueCountries.forEach((country, index) => {
            countryColors[country] = colorPalette[index % colorPalette.length];
        });

        const backgroundColors = countries.map(country => countryColors[country] + '80');
        const borderColors = countries.map(country => countryColors[country]);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: gameLabels,
                datasets: [{
                    label: 'Rating',
                    data: ratings,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    title: {
                        display: true,
                        text: '🎮 Top-Rated Games by Country',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                const index = context[0].dataIndex;
                                return sortedGames[index].title;
                            },
                            label: function(context) {
                                const index = context.dataIndex;
                                const game = sortedGames[index];
                                return [
                                    `Rating: ${game.rating}/10`,
                                    `Country: ${game.country}`,
                                    `Developer: ${game.developer || 'Unknown'}`,
                                    game.genre ? `Genre: ${game.genre}` : '',
                                    game.platform ? `Platform: ${game.platform}` : ''
                                ].filter(line => line !== '');
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Rating (out of 10)'
                        },
                        beginAtZero: true,
                        max: 10
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Games'
                        },
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        console.log('Top Games by Country Chart initialized successfully');
    } catch (error) {
        console.error('Error initializing Top Games by Country Chart:', error);
    }
}

// 7. 📦 Developer Profile Table - Interactive Table
function initializeDeveloperProfileTable() {
    try {
        console.log('Initializing Developer Profile Table');
        
        // Check if we have a container for the table
        let tableContainer = document.getElementById('developerProfileTable');
        if (!tableContainer) {
            // Create table container if it doesn't exist
            const chartsContainer = document.querySelector('.tactical-charts-container');
            if (chartsContainer) {
                tableContainer = document.createElement('div');
                tableContainer.id = 'developerProfileTable';
                tableContainer.className = 'chart-container';
                tableContainer.innerHTML = `
                    <div class="card">
                        <h5 class="card-title">📦 Developer Profile Table</h5>
                        <div class="table-controls mb-3">
                            <input type="text" id="developerSearch" placeholder="Search developers..." class="form-control" style="width: 300px; display: inline-block;">
                            <button id="exportDeveloperData" class="btn btn-primary ms-2">Export CSV</button>
                        </div>
                        <div class="table-responsive" style="max-height: 350px; overflow-y: auto;">
                            <table id="developerTable" class="table table-striped table-hover table-compact table-dark">
                                <thead class="table-dark">
                                    <tr>
                                        <th data-sort="name">Name</th>
                                        <th data-sort="studio_type">Studio Type</th>
                                        <th data-sort="country">Country</th>
                                        <th data-sort="years_active">Years Active</th>
                                        <th data-sort="replay_rate">Replay Rate</th>
                                        <th data-sort="performance_tier">Performance Tier</th>
                                    </tr>
                                </thead>
                                <tbody id="developerTableBody">
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
                chartsContainer.appendChild(tableContainer);
            }
        }

        if (!tableContainer) {
            console.warn('Could not create or find table container');
            return;
        }

        // Prepare table data from available sources
        let tableData = [];
        
        // Use real developer data if available
        if (window.tacticalDeveloperProfiles && Array.isArray(window.tacticalDeveloperProfiles)) {
            tableData = window.tacticalDeveloperProfiles.map(dev => ({
                name: dev.name || 'Unknown Developer',
                studio_type: dev.studio_type || 'Unknown',
                country: dev.country || 'Unknown',
                years_active: dev.years_active || 0,
                replay_rate: dev.replay_rate || 0,
                performance_tier: dev.performance_tier || 'Unknown',
                founded_year: dev.founded_year || 'Unknown'
            }));
        } else {
            // Fallback sample data for demonstration if no real data available
            const studioTypes = ['AAA', 'Mid-tier', 'Indie', 'Mobile'];
            const countries = ['United States', 'Japan', 'United Kingdom', 'Canada', 'Germany'];
            
            studioTypes.forEach(studioType => {
                for (let i = 0; i < 5; i++) {
                    const replayRate = 0.4 + Math.random() * 0.4;
                    tableData.push({
                        name: `${studioType} Developer ${i + 1}`,
                        studio_type: studioType,
                        country: countries[Math.floor(Math.random() * countries.length)],
                        years_active: Math.floor(Math.random() * 20) + 5,
                        replay_rate: replayRate,
                        performance_tier: getPerformanceTier(replayRate),
                        founded_year: 2024 - Math.floor(Math.random() * 20) - 5
                    });
                }
            });
        }

        // Populate table
        const tableBody = document.getElementById('developerTableBody');
        if (tableBody) {
            renderTable(tableData);
            
            // Add search functionality
            const searchInput = document.getElementById('developerSearch');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    const searchTerm = this.value.toLowerCase();
                    const filteredData = tableData.filter(row => 
                        Object.values(row).some(value => 
                            value.toString().toLowerCase().includes(searchTerm)
                        )
                    );
                    renderTable(filteredData);
                });
            }

            // Add export functionality
            const exportButton = document.getElementById('exportDeveloperData');
            if (exportButton) {
                exportButton.addEventListener('click', function() {
                    exportToCSV(tableData, 'developer_profiles.csv');
                });
            }

            // Add sorting functionality
            document.querySelectorAll('[data-sort]').forEach(header => {
                header.addEventListener('click', function() {
                    const sortKey = this.getAttribute('data-sort');
                    sortTable(tableData, sortKey);
                    renderTable(tableData);
                });
            });
        }

        function renderTable(data) {
            const tableBody = document.getElementById('developerTableBody');
            if (!tableBody) return;

            tableBody.innerHTML = data.map(row => `
                <tr>
                    <td>${row.name}</td>
                    <td><span class="badge bg-secondary">${row.studio_type}</span></td>
                    <td>${row.country}</td>
                    <td>${row.years_active} years</td>
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="progress me-2" style="width: 60px; height: 8px;">
                                <div class="progress-bar" style="width: ${row.replay_rate * 100}%"></div>
                            </div>
                            ${(row.replay_rate * 100).toFixed(1)}%
                        </div>
                    </td>
                    <td><span class="badge ${getPerformanceBadgeClass(row.performance_tier)}">${row.performance_tier}</span></td>
                </tr>
            `).join('');
        }

        function sortTable(data, key) {
            data.sort((a, b) => {
                if (typeof a[key] === 'number') {
                    return b[key] - a[key];
                }
                return a[key].localeCompare(b[key]);
            });
        }

        function exportToCSV(data, filename) {
            const headers = ['Name', 'Studio Type', 'Country', 'Years Active', 'Replay Rate', 'Performance Tier'];
            const csvContent = [
                headers.join(','),
                ...data.map(row => [
                    row.name,
                    row.studio_type,
                    row.country,
                    row.years_active,
                    (row.replay_rate * 100).toFixed(2) + '%',
                    row.performance_tier
                ].join(','))
            ].join('\n');

            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
        }

        function getPerformanceTier(replayRate) {
            if (replayRate >= 0.75) return 'Elite';
            if (replayRate >= 0.65) return 'High';
            if (replayRate >= 0.55) return 'Medium';
            if (replayRate >= 0.45) return 'Developing';
            return 'Emerging';
        }

        function getPerformanceBadgeClass(tier) {
            const classes = {
                'Elite': 'bg-success',
                'High': 'bg-info',
                'Medium': 'bg-warning',
                'Developing': 'bg-secondary',
                'Emerging': 'bg-light text-dark'
            };
            return classes[tier] || 'bg-secondary';
        }

        console.log('Developer Profile Table initialized successfully');
    } catch (error) {
        console.error('Error initializing Developer Profile Table:', error);
    }
}

// Lifecycle Dashboard Charts
function initializeLifecycleCharts() {
    console.log('Lifecycle charts initialized (placeholder)');
    // Lifecycle chart implementations would go here
}

// Evolution Dashboard Charts  
function initializeEvolutionCharts() {
    console.log('Evolution charts initialized (placeholder)');
    // Evolution chart implementations would go here
}

// Helper function to generate colors for charts
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

// Initialize all charts
function initializeCharts() {
    console.log('Initializing enhanced charts...');
    
    try {
        // Studio Performance Charts
        console.log('Initializing studio charts...');
        if (typeof initializeStudioCharts === 'function') {
            initializeStudioCharts();
        }
        
        // Operational Dashboard Charts
        console.log('Initializing operational charts...');
        if (typeof initializeOperationalCharts === 'function') {
            initializeOperationalCharts();
        }
        
        // Tactical Dashboard Charts (Developer Performance)
        console.log('Initializing tactical charts...');
        initializeTacticalCharts();
        
        // Lifecycle Dashboard Charts
        console.log('Initializing lifecycle charts...');
        initializeLifecycleCharts();
        
        // Evolution Dashboard Charts
        console.log('Initializing evolution charts...');
        initializeEvolutionCharts();
        
        console.log('All charts initialized successfully');
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
} 