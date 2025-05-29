// Advanced Charts for Tactical, Lifecycle, and Evolution Dashboards

// Tactical Dashboard Charts
function initializeTacticalCharts() {
    // Tactical Sankey Chart (Genre → Platform → Publisher Flow)
    if (tacticalSankeyData && tacticalSankeyData.length > 0) {
        const sankeyCtx = document.getElementById('tacticalSankeyChart').getContext('2d');
        
        new Chart(sankeyCtx, {
            type: 'bar',
            data: {
                labels: tacticalSankeyData.slice(0, 15).map(item => `${item.genre} → ${item.platform}`),
                datasets: [{
                    label: 'Flow Count',
                    data: tacticalSankeyData.slice(0, 15).map(item => item.count),
                    backgroundColor: generateColors(15),
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                ...commonOptions,
                indexAxis: 'y',
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Genre → Platform Flow Analysis', 
                        color: '#e94560'
                    }
                }
            }
        });
    }

    // Tactical Venn Chart (Cross-Platform Game Availability)
    if (tacticalVennData && tacticalVennData.length > 0) {
        const vennCtx = document.getElementById('tacticalVennChart').getContext('2d');
        
        new Chart(vennCtx, {
            type: 'doughnut',
            data: {
                labels: tacticalVennData.map(item => `${item.platform_count} Platform${item.platform_count > 1 ? 's' : ''}`),
                datasets: [{
                    label: 'Games Available',
                    data: tacticalVennData.map(item => item.game_count),
                    backgroundColor: generateColors(tacticalVennData.length),
                    borderColor: '#f8f8f2',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#eee', font: { family: 'Roboto', size: 10 } }
                    },
                    title: { 
                        display: true, 
                        text: 'Cross-Platform Game Distribution', 
                        color: '#e94560'
                    }
                }
            }
        });
    }

    // Tactical Chord Chart (Developer ↔ Platform ↔ Genre Connections)
    if (tacticalChordData && tacticalChordData.length > 0) {
        const chordCtx = document.getElementById('tacticalChordChart').getContext('2d');
        
        new Chart(chordCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Developer-Platform Connections',
                    data: tacticalChordData.slice(0, 50).map((item, index) => ({
                        x: index % 10,
                        y: Math.floor(index / 10),
                        r: Math.sqrt(item.count) * 3
                    })),
                    backgroundColor: generateColors(50),
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Developer-Platform-Genre Network', 
                        color: '#e94560'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const item = tacticalChordData[context.dataIndex];
                                return [
                                    `Developer: ${item.developer}`,
                                    `Platform: ${item.platform}`,
                                    `Genre: ${item.genre}`,
                                    `Games: ${item.count}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    }

    // Tactical Dumbbell Chart (Rating Range by Platform & Genre)
    if (tacticalDumbbellData && tacticalDumbbellData.length > 0) {
        const dumbbellCtx = document.getElementById('tacticalDumbbellChart').getContext('2d');
        
        new Chart(dumbbellCtx, {
            type: 'bar',
            data: {
                labels: tacticalDumbbellData.slice(0, 10).map(item => `${item.platform} - ${item.genre}`),
                datasets: [{
                    label: 'Min Rating',
                    data: tacticalDumbbellData.slice(0, 10).map(item => item.min_rating),
                    backgroundColor: '#ff5555',
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }, {
                    label: 'Max Rating',
                    data: tacticalDumbbellData.slice(0, 10).map(item => item.max_rating),
                    backgroundColor: '#50fa7b',
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    title: { 
                        display: true, 
                        text: 'Rating Range by Platform & Genre', 
                        color: '#e94560'
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: { ...commonOptions.scales.y, max: 10 }
                }
            }
        });
    }

    // Tactical Marimekko Chart (Genre & Platform Market Share Matrix)
    if (tacticalMarimekkoData && tacticalMarimekkoData.length > 0) {
        const marimekkoCtx = document.getElementById('tacticalMarimekkoChart').getContext('2d');
        
        new Chart(marimekkoCtx, {
            type: 'bar',
            data: {
                labels: tacticalMarimekkoData.slice(0, 20).map(item => `${item.genre} (${item.platform})`),
                datasets: [{
                    label: 'Market Share',
                    data: tacticalMarimekkoData.slice(0, 20).map(item => item.market_share),
                    backgroundColor: generateColors(20),
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
                        text: 'Genre & Platform Market Share Matrix', 
                        color: '#e94560'
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    x: {
                        ...commonOptions.scales.x,
                        ticks: {
                            ...commonOptions.scales.x.ticks,
                            maxRotation: 45
                        }
                    }
                }
            }
        });
    }
}

// Lifecycle Dashboard Charts
function initializeLifecycleCharts() {
    // Lifecycle Survival Chart
    if (lifecycleSurvivalData && lifecycleSurvivalData.length > 0) {
        const survivalCtx = document.getElementById('lifecycleSurvivalChart').getContext('2d');
        
        new Chart(survivalCtx, {
            type: 'line',
            data: {
                labels: lifecycleSurvivalData.map(item => `Year ${item.years_since_release}`),
                datasets: [{
                    label: 'Survival Rate (%)',
                    data: lifecycleSurvivalData.map(item => item.survival_rate),
                    borderColor: '#50fa7b',
                    backgroundColor: 'rgba(80, 250, 123, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    title: { 
                        display: true, 
                        text: 'Game Engagement Survival Over Time', 
                        color: '#e94560'
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: { 
                        ...commonOptions.scales.y, 
                        max: 100,
                        title: {
                            display: true,
                            text: 'Survival Rate (%)',
                            color: '#50fa7b'
                        }
                    }
                }
            }
        });
    }

    // Lifecycle Ridgeline Chart
    if (lifecycleRidgelineData && lifecycleRidgelineData.length > 0) {
        const ridgelineCtx = document.getElementById('lifecycleRidgelineChart').getContext('2d');
        
        const genreGroups = {};
        lifecycleRidgelineData.forEach(item => {
            if (!genreGroups[item.genre]) {
                genreGroups[item.genre] = [];
            }
            genreGroups[item.genre].push(item);
        });

        const datasets = Object.keys(genreGroups).slice(0, 8).map((genre, index) => ({
            label: genre,
            data: genreGroups[genre].map(item => ({
                x: item.rating_range,
                y: item.game_count + (index * 20)
            })),
            borderColor: generateColors(8)[index],
            backgroundColor: generateColors(8)[index] + '40',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }));

        new Chart(ridgelineCtx, {
            type: 'line',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#eee', font: { family: 'Roboto', size: 9 } }
                    },
                    title: { 
                        display: true, 
                        text: 'Rating Distribution by Genre', 
                        color: '#e94560'
                    }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'Rating Range', color: '#8be9fd' },
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    },
                    y: { 
                        title: { display: true, text: 'Game Count (Offset by Genre)', color: '#ff79c6' },
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    }
                }
            }
        });
    }

    // Lifecycle Timeline Chart
    if (lifecycleTimelineData && lifecycleTimelineData.length > 0) {
        const timelineCtx = document.getElementById('lifecycleTimelineChart').getContext('2d');
        
        new Chart(timelineCtx, {
            type: 'bubble',
            data: {
                datasets: [{
                    label: 'Most Voted Games',
                    data: lifecycleTimelineData.slice(0, 50).map(item => ({
                        x: item.release_year,
                        y: item.rating,
                        r: Math.sqrt(item.votes) / 50
                    })),
                    backgroundColor: generateColors(50),
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Most Voted Games Over Time', 
                        color: '#e94560'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const item = lifecycleTimelineData[context.dataIndex];
                                return [
                                    `Game: ${item.name}`,
                                    `Year: ${item.release_year}`,
                                    `Rating: ${item.rating}`,
                                    `Votes: ${item.votes.toLocaleString()}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'Release Year', color: '#8be9fd' },
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    },
                    y: { 
                        title: { display: true, text: 'Rating', color: '#ff79c6' },
                        max: 10,
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    }
                }
            }
        });
    }

    // Lifecycle Hexbin Chart
    if (lifecycleHexbinData && lifecycleHexbinData.length > 0) {
        const hexbinCtx = document.getElementById('lifecycleHexbinChart').getContext('2d');
        
        new Chart(hexbinCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Games Cluster',
                    data: lifecycleHexbinData.slice(0, 200).map(item => ({
                        x: item.rating,
                        y: Math.log10(item.votes + 1)
                    })),
                    backgroundColor: generateColors(200),
                    borderColor: '#f8f8f2',
                    borderWidth: 1,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Rating vs Votes Clusters', 
                        color: '#e94560'
                    }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'Rating', color: '#8be9fd' },
                        max: 10,
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    },
                    y: { 
                        title: { display: true, text: 'Log(Votes)', color: '#ff79c6' },
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    }
                }
            }
        });
    }

    // Lifecycle Parallel Chart
    if (lifecycleParallelData && lifecycleParallelData.length > 0) {
        const parallelCtx = document.getElementById('lifecycleParallelChart').getContext('2d');
        
        new Chart(parallelCtx, {
            type: 'radar',
            data: {
                labels: ['Avg Rating', 'Total Votes', 'Game Count', 'Platform Count', 'Avg Release Year'],
                datasets: lifecycleParallelData.slice(0, 6).map((item, index) => ({
                    label: item.genre,
                    data: [
                        item.avg_rating,
                        Math.log10(item.total_votes + 1) * 2,
                        Math.log10(item.game_count + 1) * 3,
                        item.platform_count,
                        (item.avg_release_year - 1980) / 4
                    ],
                    borderColor: generateColors(6)[index],
                    backgroundColor: generateColors(6)[index] + '20',
                    borderWidth: 2,
                    pointBackgroundColor: generateColors(6)[index]
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#eee', font: { family: 'Roboto', size: 9 } }
                    },
                    title: { 
                        display: true, 
                        text: 'Genre Performance Comparison', 
                        color: '#e94560'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10,
                        ticks: { color: '#eee', backdropColor: 'transparent' },
                        grid: { color: '#0f3460' },
                        angleLines: { color: '#0f3460' }
                    }
                }
            }
        });
    }
}

// Evolution Dashboard Charts
function initializeEvolutionCharts() {
    // Evolution Stream Chart
    if (evolutionStreamData && evolutionStreamData.length > 0) {
        const streamCtx = document.getElementById('evolutionStreamChart').getContext('2d');
        
        const genreYearData = {};
        evolutionStreamData.forEach(item => {
            if (!genreYearData[item.genre]) {
                genreYearData[item.genre] = {};
            }
            genreYearData[item.genre][item.year] = item.avg_rating;
        });

        const years = [...new Set(evolutionStreamData.map(item => item.year))].sort();
        const genres = Object.keys(genreYearData).slice(0, 8);

        const datasets = genres.map((genre, index) => ({
            label: genre,
            data: years.map(year => genreYearData[genre][year] || 0),
            borderColor: generateColors(8)[index],
            backgroundColor: generateColors(8)[index] + '40',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }));

        new Chart(streamCtx, {
            type: 'line',
            data: { labels: years, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#eee', font: { family: 'Roboto', size: 9 } }
                    },
                    title: { 
                        display: true, 
                        text: 'Genre Popularity Evolution Over Time', 
                        color: '#e94560'
                    }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'Year', color: '#8be9fd' },
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    },
                    y: { 
                        title: { display: true, text: 'Average Rating', color: '#ff79c6' },
                        max: 10,
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    }
                }
            }
        });
    }

    // Evolution Bubble Chart
    if (evolutionBubbleData && evolutionBubbleData.length > 0) {
        const bubbleCtx = document.getElementById('evolutionBubbleChart').getContext('2d');
        
        new Chart(bubbleCtx, {
            type: 'bubble',
            data: {
                datasets: [{
                    label: 'High-Rated Games',
                    data: evolutionBubbleData.slice(0, 100).map(item => ({
                        x: item.release_year,
                        y: item.rating,
                        r: Math.sqrt(item.votes) / 30
                    })),
                    backgroundColor: evolutionBubbleData.slice(0, 100).map((item, index) => {
                        const genreColors = {
                            'Action': '#ff5555',
                            'Adventure': '#50fa7b',
                            'RPG': '#bd93f9',
                            'Strategy': '#8be9fd',
                            'Sports': '#ffb86c',
                            'Racing': '#f1fa8c'
                        };
                        return genreColors[item.genre] || generateColors(100)[index];
                    }),
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'High-Rated Game Launches by Genre', 
                        color: '#e94560'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const item = evolutionBubbleData[context.dataIndex];
                                return [
                                    `Game: ${item.name}`,
                                    `Genre: ${item.genre}`,
                                    `Year: ${item.release_year}`,
                                    `Rating: ${item.rating}`,
                                    `Votes: ${item.votes.toLocaleString()}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'Release Year', color: '#8be9fd' },
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    },
                    y: { 
                        title: { display: true, text: 'Rating', color: '#ff79c6' },
                        max: 10,
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    }
                }
            }
        });
    }

    // Evolution Hexbin Chart
    if (evolutionHexbinData && evolutionHexbinData.length > 0) {
        const evolutionHexCtx = document.getElementById('evolutionHexbinChart').getContext('2d');
        
        new Chart(evolutionHexCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Evolution Clusters',
                    data: evolutionHexbinData.slice(0, 150).map(item => ({
                        x: item.rating,
                        y: Math.log10(item.votes + 1)
                    })),
                    backgroundColor: evolutionHexbinData.slice(0, 150).map((item) => {
                        if (item.release_year >= 2020) return '#50fa7b';
                        if (item.release_year >= 2010) return '#8be9fd';
                        if (item.release_year >= 2000) return '#ffb86c';
                        if (item.release_year >= 1990) return '#bd93f9';
                        return '#ff5555';
                    }),
                    borderColor: '#f8f8f2',
                    borderWidth: 1,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: { 
                        display: true, 
                        text: 'Votes vs Rating Evolution (Colored by Decade)', 
                        color: '#e94560'
                    }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'Rating', color: '#8be9fd' },
                        max: 10,
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    },
                    y: { 
                        title: { display: true, text: 'Log(Votes)', color: '#ff79c6' },
                        ticks: { color: '#eee' }, 
                        grid: { color: '#0f3460' } 
                    }
                }
            }
        });
    }

    // Evolution Parallel Chart
    if (evolutionParallelData && evolutionParallelData.length > 0) {
        const evolutionParallelCtx = document.getElementById('evolutionParallelChart').getContext('2d');
        
        new Chart(evolutionParallelCtx, {
            type: 'radar',
            data: {
                labels: ['Avg Rating', 'Rating Stability', 'Vote Count', 'Platform Reach', 'Longevity'],
                datasets: evolutionParallelData.slice(0, 6).map((item, index) => ({
                    label: item.genre,
                    data: [
                        item.avg_rating,
                        item.rating_stability * 10,
                        Math.log10(item.total_votes + 1) * 1.5,
                        item.platform_count,
                        (item.avg_release_year - 1980) / 4
                    ],
                    borderColor: generateColors(6)[index],
                    backgroundColor: generateColors(6)[index] + '20',
                    borderWidth: 2,
                    pointBackgroundColor: generateColors(6)[index]
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#eee', font: { family: 'Roboto', size: 9 } }
                    },
                    title: { 
                        display: true, 
                        text: 'Multi-Metric Genre Evolution Analysis', 
                        color: '#e94560'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10,
                        ticks: { color: '#eee', backdropColor: 'transparent' },
                        grid: { color: '#0f3460' },
                        angleLines: { color: '#0f3460' }
                    }
                }
            }
        });
    }

    // Evolution Tree Chart
    if (evolutionTreeData && evolutionTreeData.length > 0) {
        const treeCtx = document.getElementById('evolutionTreeChart').getContext('2d');
        
        const treeNodes = [];
        const genreMap = {};
        let nodeIndex = 0;

        evolutionTreeData.forEach(item => {
            if (!genreMap[item.genre]) {
                genreMap[item.genre] = {
                    x: nodeIndex % 6,
                    y: 0,
                    size: 0,
                    platforms: []
                };
                nodeIndex++;
            }
            genreMap[item.genre].size += item.game_count;
            genreMap[item.genre].platforms.push({
                platform: item.platform,
                count: item.game_count,
                x: genreMap[item.genre].x + (Math.random() - 0.5) * 2,
                y: 1 + Math.random() * 0.5
            });
        });

        Object.keys(genreMap).forEach(genre => {
            treeNodes.push({
                x: genreMap[genre].x,
                y: 0,
                r: Math.sqrt(genreMap[genre].size) / 3,
                label: genre,
                type: 'genre'
            });
        });

        Object.values(genreMap).forEach(genreData => {
            genreData.platforms.forEach(platform => {
                treeNodes.push({
                    x: platform.x,
                    y: platform.y,
                    r: Math.sqrt(platform.count) / 2,
                    label: platform.platform,
                    type: 'platform'
                });
            });
        });

        new Chart(treeCtx, {
            type: 'bubble',
            data: {
                datasets: [{
                    label: 'Genre Nodes',
                    data: treeNodes.filter(node => node.type === 'genre'),
                    backgroundColor: '#e94560',
                    borderColor: '#f8f8f2',
                    borderWidth: 2
                }, {
                    label: 'Platform Nodes',
                    data: treeNodes.filter(node => node.type === 'platform'),
                    backgroundColor: '#8be9fd',
                    borderColor: '#f8f8f2',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#eee', font: { family: 'Roboto', size: 10 } }
                    },
                    title: { 
                        display: true, 
                        text: 'Genre → Platform Expansion Tree', 
                        color: '#e94560'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const node = context.raw;
                                return [
                                    `${node.type}: ${node.label}`,
                                    `Size: ${Math.round(node.r * 3)}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    }
} 