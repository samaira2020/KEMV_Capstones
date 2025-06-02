// Enhanced Chart implementations for Gaming Analytics Dashboard

// Initialize all charts
function initializeCharts() {
    console.log('Initializing enhanced charts...');
    
    // Studio Performance Charts
    initializeStudioCharts();
    
    // Operational Dashboard Charts
    initializeOperationalCharts();
    
    // Tactical Dashboard Charts
    initializeTacticalCharts();
    
    // Lifecycle Dashboard Charts
    initializeLifecycleCharts();
    
    // Evolution Dashboard Charts
    initializeEvolutionCharts();
}

// Enhanced Studio Performance Charts
function initializeStudioCharts() {
    // Enhanced Platform Chart with 3D effect and animations
    if (platformCounts && platformCounts.length > 0) {
        const platformCtx = document.getElementById('platformChart').getContext('2d');
        const filteredPlatforms = filterUnwantedValues(platformCounts).slice(0, 12);
        
        new Chart(platformCtx, {
            type: 'bar',
            data: {
                labels: filteredPlatforms.map(item => item._id),
                datasets: [{
                    label: 'Number of Games',
                    data: filteredPlatforms.map(item => item.count),
                    backgroundColor: filteredPlatforms.map((item, index) => {
                        const gradient = platformCtx.createLinearGradient(0, 0, 0, 400);
                        const colors = generateColors(filteredPlatforms.length);
                        gradient.addColorStop(0, colors[index]);
                        gradient.addColorStop(1, colors[index] + '40');
                        return gradient;
                    }),
                    borderColor: '#f8f8f2',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                    hoverBackgroundColor: filteredPlatforms.map((item, index) => generateColors(filteredPlatforms.length)[index] + 'CC'),
                    hoverBorderWidth: 3
                }]
            },
            options: {
                ...commonOptions,
                animation: {
                    duration: 2000,
                    easing: 'easeInOutBounce'
                },
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: '🎮 Game Distribution by Platform (Top 12)', 
                        color: '#bd93f9',
                        font: { size: 14, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10,
                        callbacks: {
                            label: function(context) {
                                const total = filteredPlatforms.reduce((sum, item) => sum + item.count, 0);
                                const percentage = ((context.parsed.y / total) * 100).toFixed(1);
                                return [
                                    `Games: ${context.parsed.y.toLocaleString()}`,
                                    `Market Share: ${percentage}%`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ...commonOptions.scales.x,
                        ticks: {
                            ...commonOptions.scales.x.ticks,
                            maxRotation: 45,
                            font: { size: 9 }
                        }
                    },
                    y: {
                        ...commonOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Number of Games',
                            color: '#50fa7b',
                            font: { size: 12, weight: 'bold' }
                        }
                    }
                }
            }
        });
    }

    // Enhanced Genre Chart with explosion effect
    if (genreCounts && genreCounts.length > 0) {
        const genreCtx = document.getElementById('genreChart').getContext('2d');
        const filteredGenres = filterUnwantedValues(genreCounts).slice(0, 10);
        
        new Chart(genreCtx, {
            type: 'doughnut',
            data: {
                labels: filteredGenres.map(item => item._id),
                datasets: [{
                    label: 'Number of Games',
                    data: filteredGenres.map(item => item.count),
                    backgroundColor: generateColors(filteredGenres.length),
                    borderColor: '#f8f8f2',
                    borderWidth: 3,
                    hoverOffset: 15,
                    hoverBorderWidth: 4,
                    offset: filteredGenres.map((item, index) => index === 0 ? 20 : 0) // Explode largest slice
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 2000,
                    easing: 'easeOutElastic'
                },
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { 
                            color: '#f8f8f2', 
                            font: { family: 'Roboto', size: 10 },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    title: { 
                        display: true, 
                        text: '🎯 Game Distribution by Genre (Top 10)', 
                        color: '#bd93f9',
                        font: { size: 14, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10,
                        callbacks: {
                            label: function(context) {
                                const total = filteredGenres.reduce((sum, item) => sum + item.count, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return [
                                    `${context.label}: ${context.parsed.toLocaleString()} games`,
                                    `${percentage}% of total`
                                ];
                            }
                        }
                    }
                }
            }
        });
    }

    // Enhanced Games Per Year Chart with area fill and trend line
    if (gamesPerYear && gamesPerYear.length > 0) {
        const gamesPerYearCtx = document.getElementById('gamesPerYearChart').getContext('2d');
        
        // Create gradient
        const gradient = gamesPerYearCtx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(80, 250, 123, 0.8)');
        gradient.addColorStop(1, 'rgba(80, 250, 123, 0.1)');
        
        new Chart(gamesPerYearCtx, {
            type: 'line',
            data: {
                labels: gamesPerYear.map(item => item.year || item._id),
                datasets: [{
                    label: 'Games Released',
                    data: gamesPerYear.map(item => item.count),
                    borderColor: '#50fa7b',
                    backgroundColor: gradient,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#50fa7b',
                    pointBorderColor: '#f8f8f2',
                    pointBorderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: '#ff79c6',
                    borderWidth: 3
                }]
            },
            options: {
                ...commonOptions,
                animation: {
                    duration: 2500,
                    easing: 'easeInOutQuart'
                },
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: '📈 Games Released Per Year Trend', 
                        color: '#bd93f9',
                        font: { size: 14, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#50fa7b',
                        borderWidth: 2,
                        cornerRadius: 10,
                        callbacks: {
                            title: function(context) {
                                return `Year ${context[0].label}`;
                            },
                            label: function(context) {
                                return `Games Released: ${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ...commonOptions.scales.x,
                        title: {
                            display: true,
                            text: 'Release Year',
                            color: '#8be9fd',
                            font: { size: 12, weight: 'bold' }
                        }
                    },
                    y: {
                        ...commonOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Number of Games',
                            color: '#50fa7b',
                            font: { size: 12, weight: 'bold' }
                        }
                    }
                }
            }
        });
    }

    // Enhanced Publisher Share Chart with custom animations
    if (publisherCounts && publisherCounts.length > 0) {
        const publisherShareCtx = document.getElementById('publisherShareChart').getContext('2d');
        const filteredPublishers = filterUnwantedValues(publisherCounts).slice(0, 8);
        
        new Chart(publisherShareCtx, {
            type: 'polarArea',
            data: {
                labels: filteredPublishers.map(item => item._id),
                datasets: [{
                    label: 'Game Share',
                    data: filteredPublishers.map(item => item.count),
                    backgroundColor: generateColors(filteredPublishers.length).map(color => color + '80'),
                    borderColor: generateColors(filteredPublishers.length),
                    borderWidth: 3,
                    hoverBorderWidth: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 2000,
                    easing: 'easeInOutBack'
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { 
                            color: '#f8f8f2', 
                            font: { family: 'Roboto', size: 10 },
                            usePointStyle: true,
                            pointStyle: 'rectRounded'
                        }
                    },
                    title: { 
                        display: true, 
                        text: '🏢 Publisher Market Share (Top 8)', 
                        color: '#bd93f9',
                        font: { size: 14, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: { 
                            color: '#eee',
                            backdropColor: 'transparent'
                        },
                        grid: { color: '#0f3460' },
                        angleLines: { color: '#0f3460' }
                    }
                }
            }
        });
    }

    // Enhanced Average Rating by Platform Chart with color coding
    if (avgRatingPlatform && avgRatingPlatform.length > 0) {
        const avgRatingPlatformCtx = document.getElementById('avgRatingPlatformChart').getContext('2d');
        const filteredPlatforms = filterUnwantedValues(avgRatingPlatform, 'platform').slice(0, 12);
        
        new Chart(avgRatingPlatformCtx, {
            type: 'bar',
            data: {
                labels: filteredPlatforms.map(item => item.platform || item._id),
                datasets: [{
                    label: 'Average Rating',
                    data: filteredPlatforms.map(item => item.avg_rating),
                    backgroundColor: filteredPlatforms.map(item => {
                        if (item.avg_rating >= 8.5) return '#50fa7b';
                        if (item.avg_rating >= 7.5) return '#f1fa8c';
                        if (item.avg_rating >= 6.5) return '#ffb86c';
                        if (item.avg_rating >= 5.5) return '#ff79c6';
                        return '#ff5555';
                    }),
                    borderColor: '#f8f8f2',
                    borderWidth: 2,
                    borderRadius: 6,
                    hoverBorderWidth: 3
                }]
            },
            options: {
                indexAxis: 'y',
                ...commonOptions,
                animation: {
                    duration: 2000,
                    easing: 'easeInOutCubic'
                },
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: '⭐ Average Rating by Platform (Top 12)', 
                        color: '#bd93f9',
                        font: { size: 14, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10,
                        callbacks: {
                            label: function(context) {
                                const rating = context.parsed.x;
                                let quality = 'Poor';
                                if (rating >= 8.5) quality = 'Excellent';
                                else if (rating >= 7.5) quality = 'Very Good';
                                else if (rating >= 6.5) quality = 'Good';
                                else if (rating >= 5.5) quality = 'Average';
                                
                                return [
                                    `Rating: ${rating.toFixed(2)}/10`,
                                    `Quality: ${quality}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        ...commonOptions.scales.x,
                        max: 10,
                        title: {
                            display: true,
                            text: 'Average Rating',
                            color: '#50fa7b',
                            font: { size: 12, weight: 'bold' }
                        }
                    },
                    y: { 
                        ...commonOptions.scales.y,
                        ticks: {
                            ...commonOptions.scales.y.ticks,
                            font: { size: 9 }
                        }
                    }
                }
            }
        });
    }

    // Enhanced Average Rating by Developer Chart
    if (avgRatingDeveloper && avgRatingDeveloper.length > 0) {
        const avgRatingDeveloperCtx = document.getElementById('avgRatingDeveloperChart').getContext('2d');
        const filteredDevelopers = filterUnwantedValues(avgRatingDeveloper).slice(0, 10);
        
        new Chart(avgRatingDeveloperCtx, {
            type: 'radar',
            data: {
                labels: filteredDevelopers.map(item => item._id.length > 15 ? item._id.substring(0, 15) + '...' : item._id),
                datasets: [{
                    label: 'Average Rating',
                    data: filteredDevelopers.map(item => item.avg_rating),
                    borderColor: '#bd93f9',
                    backgroundColor: 'rgba(189, 147, 249, 0.2)',
                    borderWidth: 3,
                    pointBackgroundColor: '#bd93f9',
                    pointBorderColor: '#f8f8f2',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 2000,
                    easing: 'easeInOutElastic'
                },
                plugins: {
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: '👨‍💻 Top Developers by Average Rating', 
                        color: '#bd93f9',
                        font: { size: 14, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10,
                        ticks: { 
                            color: '#eee',
                            backdropColor: 'transparent',
                            font: { size: 10 }
                        },
                        grid: { color: '#0f3460' },
                        angleLines: { color: '#0f3460' },
                        pointLabels: {
                            color: '#eee',
                            font: { size: 9 }
                        }
                    }
                }
            }
        });
    }

    // Enhanced Game Type Distribution Chart
    if (gameTypeDistribution && gameTypeDistribution.length > 0) {
        const gameTypeCtx = document.getElementById('gameTypeChart').getContext('2d');
        const filteredGameTypes = filterUnwantedValues(gameTypeDistribution, 'game_type');
        
        new Chart(gameTypeCtx, {
            type: 'doughnut',
            data: {
                labels: filteredGameTypes.map(item => item.game_type),
                datasets: [{
                    label: 'Number of Games',
                    data: filteredGameTypes.map(item => item.count),
                    backgroundColor: generateColors(filteredGameTypes.length),
                    borderColor: '#f8f8f2',
                    borderWidth: 3,
                    hoverOffset: 10,
                    hoverBorderWidth: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 2000,
                    easing: 'easeOutBounce'
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { 
                            color: '#f8f8f2', 
                            font: { family: 'Roboto', size: 10 },
                            usePointStyle: true,
                            pointStyle: 'triangle'
                        }
                    },
                    title: { 
                        display: true, 
                        text: '🎮 Game Type Distribution', 
                        color: '#bd93f9',
                        font: { size: 14, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10
                    }
                }
            }
        });
    }

    // Enhanced Rating Distribution Chart with gradient bars
    if (ratingDistribution && ratingDistribution.length > 0) {
        const ratingDistCtx = document.getElementById('ratingDistributionChart').getContext('2d');
        
        new Chart(ratingDistCtx, {
            type: 'bar',
            data: {
                labels: ratingDistribution.map(item => item.rating_range),
                datasets: [{
                    label: 'Number of Games',
                    data: ratingDistribution.map(item => item.count),
                    backgroundColor: ratingDistribution.map((item, index) => {
                        const gradient = ratingDistCtx.createLinearGradient(0, 0, 0, 400);
                        const colors = ['#ff5555', '#ffb86c', '#f1fa8c', '#50fa7b', '#8be9fd', '#bd93f9'];
                        gradient.addColorStop(0, colors[index]);
                        gradient.addColorStop(1, colors[index] + '40');
                        return gradient;
                    }),
                    borderColor: '#f8f8f2',
                    borderWidth: 2,
                    borderRadius: 8,
                    hoverBorderWidth: 3
                }]
            },
            options: {
                ...commonOptions,
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuint'
                },
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: '📊 Rating Distribution Analysis', 
                        color: '#bd93f9',
                        font: { size: 14, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10,
                        callbacks: {
                            label: function(context) {
                                const total = ratingDistribution.reduce((sum, item) => sum + item.count, 0);
                                const percentage = ((context.parsed.y / total) * 100).toFixed(1);
                                return [
                                    `Games: ${context.parsed.y.toLocaleString()}`,
                                    `Percentage: ${percentage}%`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ...commonOptions.scales.x,
                        title: {
                            display: true,
                            text: 'Rating Range',
                            color: '#8be9fd',
                            font: { size: 12, weight: 'bold' }
                        }
                    },
                    y: {
                        ...commonOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Number of Games',
                            color: '#50fa7b',
                            font: { size: 12, weight: 'bold' }
                        }
                    }
                }
            }
        });
    }

    // Enhanced Director Analytics Chart with mixed chart type
    if (directorAnalytics && directorAnalytics.length > 0) {
        const directorCtx = document.getElementById('directorAnalyticsChart').getContext('2d');
        const filteredDirectors = filterUnwantedValues(directorAnalytics, 'director').slice(0, 8);
        
        new Chart(directorCtx, {
            type: 'bar',
            data: {
                labels: filteredDirectors.map(item => item.director.length > 20 ? item.director.substring(0, 20) + '...' : item.director),
                datasets: [{
                    label: 'Average Rating',
                    data: filteredDirectors.map(item => item.avg_rating),
                    backgroundColor: filteredDirectors.map((item, index) => {
                        const gradient = directorCtx.createLinearGradient(0, 0, 0, 400);
                        const color = generateColors(filteredDirectors.length)[index];
                        gradient.addColorStop(0, color);
                        gradient.addColorStop(1, color + '60');
                        return gradient;
                    }),
                    borderColor: '#f8f8f2',
                    borderWidth: 2,
                    borderRadius: 10,
                    hoverBorderWidth: 3
                }, {
                    label: 'Game Count',
                    data: filteredDirectors.map(item => item.game_count),
                    type: 'line',
                    borderColor: '#ff79c6',
                    backgroundColor: 'rgba(255, 121, 198, 0.2)',
                    borderWidth: 3,
                    pointBackgroundColor: '#ff79c6',
                    pointBorderColor: '#f8f8f2',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    yAxisID: 'y1',
                    tension: 0.4
                }]
            },
            options: {
                ...commonOptions,
                animation: {
                    duration: 2500,
                    easing: 'easeInOutBack'
                },
                plugins: {
                    ...commonOptions.plugins,
                    title: { 
                        display: true, 
                        text: '🎬 Top Directors Performance Analysis', 
                        color: '#bd93f9',
                        font: { size: 14, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10,
                        callbacks: {
                            afterLabel: function(context) {
                                const director = filteredDirectors[context.dataIndex];
                                return [
                                    `Total Votes: ${director.total_votes?.toLocaleString() || 'N/A'}`,
                                    `Rating Range: ${director.min_rating} - ${director.max_rating}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ...commonOptions.scales.x,
                        ticks: {
                            ...commonOptions.scales.x.ticks,
                            maxRotation: 45,
                            font: { size: 9 }
                        }
                    },
                    y: { 
                        ...commonOptions.scales.y, 
                        max: 10,
                        title: {
                            display: true,
                            text: 'Average Rating',
                            color: '#50fa7b',
                            font: { size: 12, weight: 'bold' }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        ticks: { color: '#f8f8f2' },
                        grid: { drawOnChartArea: false },
                        title: {
                            display: true,
                            text: 'Game Count',
                            color: '#ff79c6',
                            font: { size: 12, weight: 'bold' }
                        }
                    }
                }
            }
        });
    }
}

// Enhanced Operational Dashboard Charts
function initializeOperationalCharts() {
    // Enhanced Rating Trends Chart with multiple datasets
    if (ratingTrends && ratingTrends.length > 0) {
        const ratingTrendsCtx = document.getElementById('ratingTrendsChart').getContext('2d');
        
        // Create gradients
        const ratingGradient = ratingTrendsCtx.createLinearGradient(0, 0, 0, 400);
        ratingGradient.addColorStop(0, 'rgba(255, 121, 198, 0.8)');
        ratingGradient.addColorStop(1, 'rgba(255, 121, 198, 0.1)');
        
        const countGradient = ratingTrendsCtx.createLinearGradient(0, 0, 0, 400);
        countGradient.addColorStop(0, 'rgba(139, 233, 253, 0.6)');
        countGradient.addColorStop(1, 'rgba(139, 233, 253, 0.1)');
        
        new Chart(ratingTrendsCtx, {
            type: 'line',
            data: {
                labels: ratingTrends.map(item => item.period),
                datasets: [{
                    label: 'Average Rating',
                    data: ratingTrends.map(item => item.avg_rating),
                    borderColor: '#ff79c6',
                    backgroundColor: ratingGradient,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#ff79c6',
                    pointBorderColor: '#f8f8f2',
                    pointBorderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 10,
                    borderWidth: 4
                }, {
                    label: 'Game Count',
                    data: ratingTrends.map(item => item.game_count),
                    borderColor: '#8be9fd',
                    backgroundColor: countGradient,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#8be9fd',
                    pointBorderColor: '#f8f8f2',
                    pointBorderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 10,
                    borderWidth: 4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 3000,
                    easing: 'easeInOutQuart'
                },
                plugins: {
                    legend: {
                        labels: { 
                            color: '#f8f8f2', 
                            font: { family: 'Roboto', size: 12 },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    title: { 
                        display: true, 
                        text: '📈 Rating Trends & Release Activity Over Time', 
                        color: '#bd93f9',
                        font: { size: 16, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10,
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: { 
                        ticks: { 
                            color: '#f8f8f2', 
                            maxRotation: 45,
                            font: { size: 10 }
                        }, 
                        grid: { color: '#0f3460' },
                        title: {
                            display: true,
                            text: 'Time Period',
                            color: '#8be9fd',
                            font: { size: 12, weight: 'bold' }
                        }
                    },
                    y: { 
                        beginAtZero: true, 
                        max: 10,
                        ticks: { color: '#f8f8f2' }, 
                        grid: { color: '#0f3460' },
                        title: { 
                            display: true, 
                            text: 'Average Rating', 
                            color: '#ff79c6',
                            font: { size: 12, weight: 'bold' }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        ticks: { color: '#f8f8f2' },
                        grid: { drawOnChartArea: false },
                        title: { 
                            display: true, 
                            text: 'Game Count', 
                            color: '#8be9fd',
                            font: { size: 12, weight: 'bold' }
                        }
                    }
                }
            }
        });
    }

    // Enhanced Monthly Activity Chart with seasonal colors
    if (monthlyActivity && monthlyActivity.length > 0) {
        const monthlyActivityCtx = document.getElementById('monthlyActivityChart').getContext('2d');
        
        // Seasonal color mapping
        const seasonalColors = monthlyActivity.map((item, index) => {
            const month = index + 1;
            if (month >= 3 && month <= 5) return '#50fa7b'; // Spring - Green
            if (month >= 6 && month <= 8) return '#f1fa8c'; // Summer - Yellow
            if (month >= 9 && month <= 11) return '#ffb86c'; // Fall - Orange
            return '#8be9fd'; // Winter - Blue
        });
        
        new Chart(monthlyActivityCtx, {
            type: 'bar',
            data: {
                labels: monthlyActivity.map(item => item.month_name),
                datasets: [{
                    label: 'Total Releases',
                    data: monthlyActivity.map(item => item.total_releases),
                    backgroundColor: seasonalColors.map(color => color + '80'),
                    borderColor: seasonalColors,
                    borderWidth: 3,
                    borderRadius: 8,
                    hoverBorderWidth: 4,
                    hoverBackgroundColor: seasonalColors
                }]
            },
            options: {
                ...commonOptions,
                animation: {
                    duration: 2000,
                    easing: 'easeInOutBounce'
                },
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: '🗓️ Seasonal Game Release Patterns', 
                        color: '#bd93f9',
                        font: { size: 16, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10,
                        callbacks: {
                            label: function(context) {
                                const item = monthlyActivity[context.dataIndex];
                                const season = context.dataIndex >= 2 && context.dataIndex <= 4 ? 'Spring' :
                                             context.dataIndex >= 5 && context.dataIndex <= 7 ? 'Summer' :
                                             context.dataIndex >= 8 && context.dataIndex <= 10 ? 'Fall' : 'Winter';
                                return [
                                    `Releases: ${item.total_releases.toLocaleString()}`,
                                    `Season: ${season}`,
                                    `Avg Rating: ${item.avg_rating?.toFixed(2) || 'N/A'}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ...commonOptions.scales.x,
                        title: {
                            display: true,
                            text: 'Month',
                            color: '#8be9fd',
                            font: { size: 12, weight: 'bold' }
                        }
                    },
                    y: {
                        ...commonOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Total Releases',
                            color: '#50fa7b',
                            font: { size: 12, weight: 'bold' }
                        }
                    }
                }
            }
        });
    }

    // Enhanced Platform Performance Chart with performance indicators
    if (platformPerformance && platformPerformance.length > 0) {
        const platformPerformanceCtx = document.getElementById('platformPerformanceChart').getContext('2d');
        const filteredPlatformPerf = filterUnwantedValues(platformPerformance, 'platform').slice(0, 12);
        
        filteredPlatformPerf.sort((a, b) => b.avg_rating - a.avg_rating);
        
        new Chart(platformPerformanceCtx, {
            type: 'bar',
            data: {
                labels: filteredPlatformPerf.map(item => item.platform),
                datasets: [{
                    label: 'Average Rating',
                    data: filteredPlatformPerf.map(item => item.avg_rating),
                    backgroundColor: filteredPlatformPerf.map((item) => {
                        if (item.avg_rating >= 8.5) return '#50fa7b'; // Excellent
                        if (item.avg_rating >= 7.5) return '#f1fa8c'; // Very Good
                        if (item.avg_rating >= 6.5) return '#ffb86c'; // Good
                        if (item.avg_rating >= 5.5) return '#ff79c6'; // Average
                        return '#ff5555'; // Poor
                    }),
                    borderColor: '#f8f8f2',
                    borderWidth: 2,
                    borderRadius: 10,
                    hoverBorderWidth: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 2500,
                    easing: 'easeInOutElastic'
                },
                plugins: {
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: '🏆 Platform Performance Leaderboard', 
                        color: '#bd93f9',
                        font: { size: 16, weight: 'bold' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(40, 42, 54, 0.95)',
                        titleColor: '#f8f8f2',
                        bodyColor: '#f8f8f2',
                        borderColor: '#bd93f9',
                        borderWidth: 2,
                        cornerRadius: 10,
                        callbacks: {
                            title: function(context) {
                                return `🎮 ${context[0].label}`;
                            },
                            label: function(context) {
                                const platform = filteredPlatformPerf[context.dataIndex];
                                let performance = 'Poor';
                                if (platform.avg_rating >= 8.5) performance = '🏆 Excellent';
                                else if (platform.avg_rating >= 7.5) performance = '🥈 Very Good';
                                else if (platform.avg_rating >= 6.5) performance = '🥉 Good';
                                else if (platform.avg_rating >= 5.5) performance = '📊 Average';
                                
                                return [
                                    `Rating: ${platform.avg_rating.toFixed(2)}/10`,
                                    `Performance: ${performance}`,
                                    `Total Games: ${platform.total_games.toLocaleString()}`,
                                    `Rating Range: ${platform.min_rating} - ${platform.max_rating}`,
                                    `Total Votes: ${platform.total_votes ? platform.total_votes.toLocaleString() : 'N/A'}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        beginAtZero: true, 
                        max: 10,
                        ticks: { color: '#f8f8f2' }, 
                        grid: { color: '#0f3460' },
                        title: { 
                            display: true, 
                            text: 'Average Rating', 
                            color: '#50fa7b',
                            font: { size: 12, weight: 'bold' }
                        }
                    },
                    y: { 
                        ticks: { 
                            color: '#f8f8f2',
                            font: { size: 10 }
                        }, 
                        grid: { color: '#0f3460' }
                    }
                }
            }
        });
    }
} 