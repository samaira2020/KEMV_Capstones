// Chart implementations for Gaming Analytics Dashboard

// Initialize all charts
function initializeCharts() {
    console.log('Initializing charts...');
    
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

// Studio Performance Charts
function initializeStudioCharts() {
    // Platform Chart
    if (platformCounts && platformCounts.length > 0) {
        const platformCtx = document.getElementById('platformChart').getContext('2d');
        const filteredPlatforms = filterUnwantedValues(platformCounts).slice(0, 10);
        new Chart(platformCtx, {
            type: 'bar',
            data: {
                labels: filteredPlatforms.map(item => item._id),
                datasets: [{
                    label: 'Number of Games',
                    data: filteredPlatforms.map(item => item.count),
                    backgroundColor: generateColors(filteredPlatforms.length),
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Game Distribution by Platform (Top 10)', 
                        color: '#bd93f9'
                    }
                }
            }
        });
    }

    // Genre Chart
    if (genreCounts && genreCounts.length > 0) {
        const genreCtx = document.getElementById('genreChart').getContext('2d');
        const filteredGenres = filterUnwantedValues(genreCounts).slice(0, 10);
        new Chart(genreCtx, {
            type: 'pie',
            data: {
                labels: filteredGenres.map(item => item._id),
                datasets: [{
                    label: 'Number of Games',
                    data: filteredGenres.map(item => item.count),
                    backgroundColor: generateColors(filteredGenres.length),
                    borderColor: '#f8f8f2',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 1000 },
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#f8f8f2', font: { family: 'Roboto', size: 10 } }
                    },
                    title: { 
                        display: true, 
                        text: 'Game Distribution by Genre (Top 10)', 
                        color: '#bd93f9'
                    }
                }
            }
        });
    }

    // Games Per Year Chart
    if (gamesPerYear && gamesPerYear.length > 0) {
        const gamesPerYearCtx = document.getElementById('gamesPerYearChart').getContext('2d');
        new Chart(gamesPerYearCtx, {
            type: 'line',
            data: {
                labels: gamesPerYear.map(item => item.year || item._id),
                datasets: [{
                    label: 'Number of Games',
                    data: gamesPerYear.map(item => item.count),
                    borderColor: '#50fa7b',
                    backgroundColor: 'rgba(80, 250, 123, 0.2)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#50fa7b',
                    pointBorderColor: '#f8f8f2',
                    pointBorderWidth: 2
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Games Released Per Year', 
                        color: '#bd93f9'
                    }
                }
            }
        });
    }

    // Publisher Share Chart
    if (publisherCounts && publisherCounts.length > 0) {
        const publisherShareCtx = document.getElementById('publisherShareChart').getContext('2d');
        const filteredPublishers = filterUnwantedValues(publisherCounts).slice(0, 10);
        
        new Chart(publisherShareCtx, {
            type: 'doughnut',
            data: {
                labels: filteredPublishers.map(item => item._id),
                datasets: [{
                    label: 'Game Share',
                    data: filteredPublishers.map(item => item.count),
                    backgroundColor: generateColors(filteredPublishers.length),
                    borderColor: '#f8f8f2',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 1000 },
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#f8f8f2', font: { family: 'Roboto', size: 10 } }
                    },
                    title: { 
                        display: true, 
                        text: 'Game Share by Publisher (Top 10)', 
                        color: '#bd93f9'
                    }
                }
            }
        });
    }

    // Average Rating by Platform Chart
    if (avgRatingPlatform && avgRatingPlatform.length > 0) {
        const avgRatingPlatformCtx = document.getElementById('avgRatingPlatformChart').getContext('2d');
        const filteredPlatforms = filterUnwantedValues(avgRatingPlatform, 'platform').slice(0, 10);
        new Chart(avgRatingPlatformCtx, {
            type: 'bar',
            data: {
                labels: filteredPlatforms.map(item => item.platform || item._id),
                datasets: [{
                    label: 'Average Rating',
                    data: filteredPlatforms.map(item => item.avg_rating),
                    backgroundColor: generateColors(filteredPlatforms.length),
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Average Rating by Platform (Top 10)', 
                        color: '#bd93f9'
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: { ...commonOptions.scales.y, max: 10 }
                }
            }
        });
    }

    // Average Rating by Developer Chart
    if (avgRatingDeveloper && avgRatingDeveloper.length > 0) {
        const avgRatingDeveloperCtx = document.getElementById('avgRatingDeveloperChart').getContext('2d');
        const filteredDevelopers = filterUnwantedValues(avgRatingDeveloper).slice(0, 10);
        new Chart(avgRatingDeveloperCtx, {
            type: 'bar',
            data: {
                labels: filteredDevelopers.map(item => item._id),
                datasets: [{
                    label: 'Average Rating',
                    data: filteredDevelopers.map(item => item.avg_rating),
                    backgroundColor: generateColors(filteredDevelopers.length),
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Average Rating by Developer (Top 10)', 
                        color: '#bd93f9'
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: { ...commonOptions.scales.y, max: 10 },
                    x: {
                        ...commonOptions.scales.x,
                        ticks: {
                            ...commonOptions.scales.x.ticks,
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            }
        });
    }

    // Game Type Distribution Chart
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
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 1000 },
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#f8f8f2', font: { family: 'Roboto', size: 10 } }
                    },
                    title: { 
                        display: true, 
                        text: 'Game Distribution', 
                        color: '#bd93f9'
                    }
                }
            }
        });
    }

    // Rating Distribution Chart
    if (ratingDistribution && ratingDistribution.length > 0) {
        const ratingDistCtx = document.getElementById('ratingDistributionChart').getContext('2d');
        new Chart(ratingDistCtx, {
            type: 'bar',
            data: {
                labels: ratingDistribution.map(item => item.rating_range),
                datasets: [{
                    label: 'Number of Games',
                    data: ratingDistribution.map(item => item.count),
                    backgroundColor: [
                        '#ff5555', '#ffb86c', '#f1fa8c', '#50fa7b', '#8be9fd', '#bd93f9'
                    ],
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Rating Distribution', 
                        color: '#bd93f9'
                    }
                }
            }
        });
    }

    // Director Analytics Chart
    if (directorAnalytics && directorAnalytics.length > 0) {
        const directorCtx = document.getElementById('directorAnalyticsChart').getContext('2d');
        const filteredDirectors = filterUnwantedValues(directorAnalytics, 'director').slice(0, 10);
        new Chart(directorCtx, {
            type: 'bar',
            data: {
                labels: filteredDirectors.map(item => item.director),
                datasets: [{
                    label: 'Average Rating',
                    data: filteredDirectors.map(item => item.avg_rating),
                    backgroundColor: generateColors(filteredDirectors.length),
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Top Directors by Average Rating', 
                        color: '#bd93f9'
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                const director = filteredDirectors[context.dataIndex];
                                return `Games: ${director.game_count}, Total Votes: ${director.total_votes}`;
                            }
                        }
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: { ...commonOptions.scales.y, max: 10 },
                    x: {
                        ...commonOptions.scales.x,
                        ticks: {
                            ...commonOptions.scales.x.ticks,
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            }
        });
    }
}

// Operational Dashboard Charts
function initializeOperationalCharts() {
    // Rating Trends Chart
    if (ratingTrends && ratingTrends.length > 0) {
        const ratingTrendsCtx = document.getElementById('ratingTrendsChart').getContext('2d');
        new Chart(ratingTrendsCtx, {
            type: 'line',
            data: {
                labels: ratingTrends.map(item => item.period),
                datasets: [{
                    label: 'Average Rating',
                    data: ratingTrends.map(item => item.avg_rating),
                    borderColor: '#ff79c6',
                    backgroundColor: 'rgba(255, 121, 198, 0.2)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#ff79c6',
                    pointBorderColor: '#f8f8f2',
                    pointBorderWidth: 2
                }, {
                    label: 'Game Count',
                    data: ratingTrends.map(item => item.game_count),
                    borderColor: '#8be9fd',
                    backgroundColor: 'rgba(139, 233, 253, 0.2)',
                    tension: 0.4,
                    fill: false,
                    pointBackgroundColor: '#8be9fd',
                    pointBorderColor: '#f8f8f2',
                    pointBorderWidth: 2,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 1000 },
                plugins: {
                    legend: {
                        labels: { color: '#f8f8f2', font: { family: 'Roboto', size: 11 } }
                    },
                    title: { 
                        display: true, 
                        text: 'Rating Trends Over Time', 
                        color: '#bd93f9'
                    }
                },
                scales: {
                    x: { 
                        ticks: { color: '#f8f8f2', maxRotation: 45 }, 
                        grid: { color: '#0f3460' } 
                    },
                    y: { 
                        beginAtZero: true, 
                        max: 10,
                        ticks: { color: '#f8f8f2' }, 
                        grid: { color: '#0f3460' },
                        title: { display: true, text: 'Average Rating', color: '#ff79c6' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        ticks: { color: '#f8f8f2' },
                        grid: { drawOnChartArea: false },
                        title: { display: true, text: 'Game Count', color: '#8be9fd' }
                    }
                }
            }
        });
    }

    // Monthly Activity Chart
    if (monthlyActivity && monthlyActivity.length > 0) {
        const monthlyActivityCtx = document.getElementById('monthlyActivityChart').getContext('2d');
        new Chart(monthlyActivityCtx, {
            type: 'bar',
            data: {
                labels: monthlyActivity.map(item => item.month_name),
                datasets: [{
                    label: 'Total Releases',
                    data: monthlyActivity.map(item => item.total_releases),
                    backgroundColor: generateColors(monthlyActivity.length),
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Game Releases by Month', 
                        color: '#bd93f9'
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    x: {
                        ...commonOptions.scales.x,
                        ticks: {
                            ...commonOptions.scales.x.ticks,
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            }
        });
    }

    // Platform Performance Chart
    if (platformPerformance && platformPerformance.length > 0) {
        const platformPerformanceCtx = document.getElementById('platformPerformanceChart').getContext('2d');
        const filteredPlatformPerf = filterUnwantedValues(platformPerformance, 'platform').slice(0, 10);
        
        filteredPlatformPerf.sort((a, b) => b.avg_rating - a.avg_rating);
        
        new Chart(platformPerformanceCtx, {
            type: 'bar',
            data: {
                labels: filteredPlatformPerf.map(item => item.platform),
                datasets: [{
                    label: 'Average Rating',
                    data: filteredPlatformPerf.map(item => item.avg_rating),
                    backgroundColor: filteredPlatformPerf.map((item) => {
                        if (item.avg_rating >= 8) return '#50fa7b';
                        if (item.avg_rating >= 7) return '#f1fa8c';
                        if (item.avg_rating >= 6) return '#ffb86c';
                        return '#ff5555';
                    }),
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 1000 },
                plugins: {
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Top Platforms by Average Rating', 
                        color: '#bd93f9'
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return context[0].label;
                            },
                            label: function(context) {
                                const platform = filteredPlatformPerf[context.dataIndex];
                                return [
                                    `Average Rating: ${platform.avg_rating}/10`,
                                    `Total Games: ${platform.total_games}`,
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
                        title: { display: true, text: 'Average Rating', color: '#50fa7b' }
                    },
                    y: { 
                        ticks: { color: '#f8f8f2' }, 
                        grid: { color: '#0f3460' }
                    }
                }
            }
        });
    }
} 