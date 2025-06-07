// Advanced Charts for Tactical, Lifecycle, and Evolution Dashboards

// Enhanced Developer Performance Dashboard Charts
function initializeTacticalCharts() {
    console.log('Initializing developer performance dashboard charts...');
    console.log('Developer performance data available:', {
        studio: tacticalSankeyData?.length || 0,
        geographic: tacticalVennData?.length || 0,
        maturity: tacticalChordData?.length || 0,
        replayRate: tacticalDumbbellData?.length || 0,
        matrix: tacticalMarimekkoData?.length || 0
    });
    
    // 1. Studio Type Performance Analysis
    if (tacticalSankeyData && tacticalSankeyData.length > 0) {
        console.log('Initializing Studio Type Performance Analysis...');
        const sankeyCtx = document.getElementById('tacticalSankeyChart');
        if (!sankeyCtx) {
            console.error('tacticalSankeyChart canvas not found');
            return;
        }
        
        try {
            const ctx = sankeyCtx.getContext('2d');
            
            // Process studio performance data
            const studioData = tacticalSankeyData.slice(0, 8); // Limit to top 8 studio types
            const labels = studioData.map(item => item.studio_type);
            const replayRates = studioData.map(item => item.avg_replay_rate);
            const developerCounts = studioData.map(item => item.developer_count);
            const yearsActive = studioData.map(item => item.avg_years_active || 0);
            
            // Create bubble chart showing studio performance
            const bubbleData = studioData.map((item, index) => ({
                x: item.avg_replay_rate,
                y: item.avg_years_active || 15,
                r: Math.sqrt(item.developer_count) * 3 + 5, // Scale bubble size
                label: item.studio_type,
                developerCount: item.developer_count
            }));
            
            new Chart(ctx, {
                type: 'bubble',
                data: {
                    datasets: [{
                        label: 'Studio Performance',
                        data: bubbleData,
                        backgroundColor: [
                            '#ff6b6b80', '#4ecdc480', '#45b7d180', '#96ceb480', 
                            '#feca5780', '#ff9ff380', '#6c5ce780', '#a8e6cf80'
                        ],
                        borderColor: [
                            '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', 
                            '#feca57', '#ff9ff3', '#6c5ce7', '#a8e6cf'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 2500,
                        easing: 'easeInOutQuart'
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Average Replay Rate',
                                color: '#f8f8f2',
                                font: { size: 12, weight: 'bold' }
                            },
                            grid: { color: '#44475a' },
                            ticks: { color: '#f8f8f2' }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Average Years Active',
                                color: '#f8f8f2',
                                font: { size: 12, weight: 'bold' }
                            },
                            grid: { color: '#44475a' },
                            ticks: { color: '#f8f8f2' }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: '🏢 Studio Type Performance Analysis',
                            color: '#bd93f9',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            display: false
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
                                    return context[0].raw.label;
                                },
                                label: function(context) {
                                    const data = context.raw;
                                    return [
                                        `Replay Rate: ${data.x.toFixed(3)}`,
                                        `Years Active: ${data.y.toFixed(1)}`,
                                        `Developers: ${data.developerCount}`,
                                        `Performance: ${data.x > 0.7 ? 'High' : data.x > 0.5 ? 'Medium' : 'Low'}`
                                    ];
                                }
                            }
                        }
                    }
                }
            });
            console.log('Studio Type Performance Analysis initialized successfully');
        } catch (error) {
            console.error('Error initializing Studio Type Performance Analysis:', error);
        }
    }

    // 2. Developer Geographic Distribution
    if (tacticalVennData && tacticalVennData.length > 0) {
        console.log('Initializing Developer Geographic Distribution...');
        const vennCtx = document.getElementById('tacticalVennChart');
        if (!vennCtx) {
            console.error('tacticalVennChart canvas not found');
            return;
        }
        
        try {
            const ctx = vennCtx.getContext('2d');
            
            // Process geographic data
            const geoData = tacticalVennData.slice(0, 10); // Top 10 countries
            const labels = geoData.map(item => item.country);
            const developerCounts = geoData.map(item => item.developer_count);
            const avgReplayRates = geoData.map(item => item.avg_replay_rate || 0);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Developer Count',
                            data: developerCounts,
                            backgroundColor: '#4ecdc480',
                            borderColor: '#4ecdc4',
                            borderWidth: 2,
                            borderRadius: 6,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Avg Replay Rate',
                            data: avgReplayRates,
                            type: 'line',
                            backgroundColor: '#ff6b6b',
                            borderColor: '#ff6b6b',
                            borderWidth: 3,
                            pointBackgroundColor: '#ff6b6b',
                            pointBorderColor: '#282a36',
                            pointBorderWidth: 2,
                            pointRadius: 6,
                            yAxisID: 'y1',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutQuart'
                    },
                    scales: {
                        x: {
                            grid: { color: '#44475a' },
                            ticks: { 
                                color: '#f8f8f2',
                                maxRotation: 45
                            }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Developer Count',
                                color: '#4ecdc4',
                                font: { size: 12, weight: 'bold' }
                            },
                            grid: { color: '#44475a' },
                            ticks: { color: '#f8f8f2' }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Average Replay Rate',
                                color: '#ff6b6b',
                                font: { size: 12, weight: 'bold' }
                            },
                            grid: { drawOnChartArea: false },
                            ticks: { color: '#f8f8f2' }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: '🌍 Developer Geographic Distribution',
                            color: '#bd93f9',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            labels: {
                                color: '#f8f8f2',
                                font: { size: 11 },
                                usePointStyle: true
                            }
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
                                    if (context.datasetIndex === 0) {
                                        return `Developers: ${context.parsed.y}`;
                                    } else {
                                        return `Avg Replay Rate: ${context.parsed.y.toFixed(3)}`;
                                    }
                                }
                            }
                        }
                    }
                }
            });
            console.log('Developer Geographic Distribution initialized successfully');
        } catch (error) {
            console.error('Error initializing Developer Geographic Distribution:', error);
        }
    }

    // 3. Developer Maturity vs Performance Analysis
    if (tacticalChordData && tacticalChordData.length > 0) {
        console.log('Initializing Developer Maturity vs Performance Analysis...');
        console.log('Developer maturity data sample:', tacticalChordData.slice(0, 3));
        const chordCtx = document.getElementById('tacticalChordChart');
        if (!chordCtx) {
            console.error('tacticalChordChart canvas not found');
            return;
        }
        
        try {
            const ctx = chordCtx.getContext('2d');
            
            // Process maturity data for scatter plot
            const maturityData = tacticalChordData.slice(0, 50); // Limit for performance
            console.log('Maturity data processed:', maturityData.length, 'developers');
            
            if (maturityData.length === 0) {
                console.warn('No maturity data available');
                return;
            }
            
            // Validate data structure
            if (!maturityData.every(item => item.years_active && item.replay_rate && item.maturity_level)) {
                console.error('Invalid data structure in tacticalChordData');
                return;
            }
            
            // Group by maturity level for different colors
            const maturityGroups = {
                'Veteran': { data: [], color: '#ff6b6b' },
                'Established': { data: [], color: '#4ecdc4' },
                'Emerging': { data: [], color: '#45b7d1' }
            };
            
            maturityData.forEach(item => {
                const group = maturityGroups[item.maturity_level];
                if (group) {
                    group.data.push({
                        x: item.years_active,
                        y: item.replay_rate,
                        label: item.name,
                        studio_type: item.studio_type,
                        country: item.country
                    });
                }
            });
            
            // Create datasets for each maturity level
            const datasets = Object.keys(maturityGroups).map(level => ({
                label: level,
                data: maturityGroups[level].data,
                backgroundColor: maturityGroups[level].color + '80',
                borderColor: maturityGroups[level].color,
                borderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }));
            
            new Chart(ctx, {
                type: 'scatter',
                data: { datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutQuart'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: '⏳ Developer Maturity vs Performance',
                            color: '#bd93f9',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            labels: {
                                color: '#f8f8f2',
                                font: { size: 11 },
                                usePointStyle: true
                            }
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
                                    return context[0].raw.label || 'Developer';
                                },
                                label: function(context) {
                                    const data = context.raw;
                                    return [
                                        `Years Active: ${data.x}`,
                                        `Replay Rate: ${data.y.toFixed(3)}`,
                                        `Studio Type: ${data.studio_type || 'Unknown'}`,
                                        `Country: ${data.country || 'Unknown'}`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Years Active',
                                color: '#f8f8f2',
                                font: { size: 12, weight: 'bold' }
                            },
                            grid: { color: '#44475a' },
                            ticks: { color: '#f8f8f2' }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Replay Rate',
                                color: '#f8f8f2',
                                font: { size: 12, weight: 'bold' }
                            },
                            grid: { color: '#44475a' },
                            ticks: { color: '#f8f8f2' }
                        }
                    }
                }
            });
            console.log('Developer Maturity vs Performance Analysis initialized successfully');
        } catch (error) {
            console.error('Error initializing Developer Maturity vs Performance Analysis:', error);
        }
    } else {
        console.log('No developer maturity data available - length:', tacticalChordData ? tacticalChordData.length : 'undefined');
    }

    // 4. Replay Rate Distribution by Studio Type (Dumbbell Chart)
    if (tacticalDumbbellData && tacticalDumbbellData.length > 0) {
        console.log('Initializing Replay Rate Distribution Analysis...');
        const dumbbellCtx = document.getElementById('tacticalDumbbellChart');
        if (!dumbbellCtx) {
            console.error('tacticalDumbbellChart canvas not found');
            return;
        }
        
        try {
            const ctx = dumbbellCtx.getContext('2d');
            
            const replayData = tacticalDumbbellData.slice(0, 8);
            
            // Create dumbbell chart using multiple datasets
            const datasets = [
                {
                    label: 'Minimum Replay Rate',
                    data: replayData.map(item => item.min_replay_rate),
                    backgroundColor: '#ff6b6b80',
                    borderColor: '#ff6b6b',
                    borderWidth: 2,
                    pointRadius: 8,
                    pointStyle: 'circle',
                    type: 'line',
                    tension: 0,
                    order: 3
                },
                {
                    label: 'Maximum Replay Rate',
                    data: replayData.map(item => item.max_replay_rate),
                    backgroundColor: '#50fa7b80',
                    borderColor: '#50fa7b',
                    borderWidth: 2,
                    pointRadius: 8,
                    pointStyle: 'circle',
                    type: 'line',
                    tension: 0,
                    order: 2
                },
                {
                    label: 'Average Replay Rate',
                    data: replayData.map(item => item.avg_replay_rate),
                    backgroundColor: '#bd93f9',
                    borderColor: '#f8f8f2',
                    borderWidth: 3,
                    pointRadius: 10,
                    pointStyle: 'rectRot',
                    type: 'line',
                    tension: 0,
                    order: 1
                }
            ];
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: replayData.map(item => item.studio_type),
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 2500,
                        easing: 'easeInOutQuart'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: '🔁 Replay Rate Distribution by Studio Type',
                            color: '#bd93f9',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            labels: {
                                color: '#f8f8f2',
                                font: { size: 11 },
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(40, 42, 54, 0.95)',
                            titleColor: '#f8f8f2',
                            bodyColor: '#f8f8f2',
                            borderColor: '#bd93f9',
                            borderWidth: 2,
                            cornerRadius: 10,
                            callbacks: {
                                afterTitle: function(context) {
                                    const item = replayData[context[0].dataIndex];
                                    return `Developers: ${item.developer_count}`;
                                },
                                label: function(context) {
                                    const value = context.parsed.y.toFixed(3);
                                    return `${context.dataset.label}: ${value}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: '#44475a' },
                            ticks: { 
                                color: '#f8f8f2',
                                maxRotation: 45
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Replay Rate',
                                color: '#f8f8f2',
                                font: { size: 12, weight: 'bold' }
                            },
                            grid: { color: '#44475a' },
                            ticks: { color: '#f8f8f2' }
                        }
                    }
                }
            });
            console.log('Replay Rate Distribution Analysis initialized successfully');
        } catch (error) {
            console.error('Error initializing Replay Rate Distribution Analysis:', error);
        }
    }

    // 5. Country vs Studio Type Matrix (Heatmap)
    if (tacticalMarimekkoData && tacticalMarimekkoData.length > 0) {
        console.log('Initializing Country vs Studio Type Matrix...');
        const marimekkoCtx = document.getElementById('tacticalMarimekkoChart');
        if (!marimekkoCtx) {
            console.error('tacticalMarimekkoChart canvas not found');
            return;
        }
        
        try {
            const ctx = marimekkoCtx.getContext('2d');
            
            // Process matrix data for heatmap
            const matrixData = tacticalMarimekkoData.slice(0, 20); // Limit for readability
            console.log('Matrix data processed:', matrixData.length, 'combinations');
            
            if (matrixData.length === 0) {
                console.warn('No matrix data available');
                return;
            }
            
            // Validate data structure
            if (!matrixData.every(item => item.country && item.studio_type && typeof item.developer_count === 'number')) {
                console.error('Invalid data structure in tacticalMarimekkoData');
                return;
            }
            
            // Create heatmap visualization
            const labels = matrixData.map(item => `${item.country.substring(0, 8)}... × ${item.studio_type}`);
            const data = matrixData.map(item => item.developer_count);
            const replayRates = matrixData.map(item => item.avg_replay_rate || 0);
            
            console.log('Matrix chart labels:', labels.slice(0, 3));
            console.log('Matrix chart data:', data.slice(0, 3));
            
            // Color code by developer count intensity
            const backgroundColors = data.map(count => {
                if (count > 100) return '#ff6b6b80';
                if (count > 50) return '#feca5780';
                if (count > 20) return '#4ecdc480';
                return '#45b7d180';
            });
            const borderColors = data.map(count => {
                if (count > 100) return '#ff6b6b';
                if (count > 50) return '#feca57';
                if (count > 20) return '#4ecdc4';
                return '#45b7d1';
            });
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Developer Count',
                        data: data,
                        backgroundColor: backgroundColors,
                        borderColor: borderColors,
                        borderWidth: 2,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutQuart'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: '🔥 Country vs Studio Type Matrix',
                            color: '#bd93f9',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            display: false
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
                                    const item = matrixData[context.dataIndex];
                                    return `${item.country} × ${item.studio_type}`;
                                },
                                label: function(context) {
                                    const item = matrixData[context.dataIndex];
                                    const totalDevs = matrixData.reduce((sum, d) => sum + d.developer_count, 0);
                                    const marketShare = ((item.developer_count / totalDevs) * 100).toFixed(2);
                                    const intensity = item.developer_count > 100 ? 'Very High' : 
                                                    item.developer_count > 50 ? 'High' : 
                                                    item.developer_count > 20 ? 'Medium' : 'Low';
                                    return [
                                        `Developers: ${item.developer_count}`,
                                        `Market Share: ${marketShare}%`,
                                        `Avg Replay Rate: ${(item.avg_replay_rate || 0).toFixed(3)}`,
                                        `Concentration: ${intensity}`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: '#f8f8f2',
                                font: { size: 9 },
                                maxRotation: 45
                            },
                            grid: { color: '#44475a' },
                            title: {
                                display: true,
                                text: 'Country × Studio Type Combinations',
                                color: '#8be9fd',
                                font: { size: 12, weight: 'bold' }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#f8f8f2' },
                            grid: { color: '#44475a' },
                            title: {
                                display: true,
                                text: 'Number of Developers',
                                color: '#ff79c6',
                                font: { size: 12, weight: 'bold' }
                            }
                        }
                    }
                }
            });
            console.log('Country vs Studio Type Matrix initialized successfully');
        } catch (error) {
            console.error('Error initializing Country vs Studio Type Matrix:', error);
        }
    } else {
        console.log('No country-studio matrix data available - length:', tacticalMarimekkoData ? tacticalMarimekkoData.length : 'undefined');
    }

    // 6. Developer Performance Metrics (Radar Chart)
    if (tacticalSankeyData && tacticalDumbbellData && tacticalVennData) {
        console.log('Initializing Developer Performance Metrics...');
        const focusCtx = document.getElementById('tacticalFocusChart');
        if (!focusCtx) {
            console.error('tacticalFocusChart canvas not found');
            return;
        }
        
        try {
            const ctx = focusCtx.getContext('2d');
            
            // Aggregate performance metrics by studio type
            const performanceMetrics = {};
            
            // Process studio performance data
            if (tacticalSankeyData.length > 0) {
                tacticalSankeyData.forEach(item => {
                    if (!performanceMetrics[item.studio_type]) {
                        performanceMetrics[item.studio_type] = {
                            avgReplayRate: 0,
                            developerCount: 0,
                            avgYearsActive: 0,
                            marketPresence: 0,
                            qualityScore: 0
                        };
                    }
                    performanceMetrics[item.studio_type].avgReplayRate = item.avg_replay_rate || 0;
                    performanceMetrics[item.studio_type].developerCount = item.developer_count || 0;
                    performanceMetrics[item.studio_type].avgYearsActive = item.avg_years_active || 0;
                });
            }
            
            // Add geographic diversity from venn data
            if (tacticalVennData.length > 0) {
                const studioCountries = {};
                tacticalVennData.forEach(item => {
                    // This would need studio type info, using placeholder logic
                    Object.keys(performanceMetrics).forEach(studioType => {
                        if (!studioCountries[studioType]) studioCountries[studioType] = new Set();
                        studioCountries[studioType].add(item.country);
                    });
                });
                
                Object.keys(performanceMetrics).forEach(studioType => {
                    performanceMetrics[studioType].marketPresence = studioCountries[studioType]?.size || 1;
                });
            }
            
            // Add quality metrics from dumbbell data
            if (tacticalDumbbellData.length > 0) {
                tacticalDumbbellData.forEach(item => {
                    if (performanceMetrics[item.studio_type]) {
                        performanceMetrics[item.studio_type].qualityScore = item.avg_replay_rate * 10;
                    }
                });
            }
            
            // Normalize values to 0-10 scale
            const maxValues = {
                avgReplayRate: Math.max(...Object.values(performanceMetrics).map(m => m.avgReplayRate)),
                developerCount: Math.max(...Object.values(performanceMetrics).map(m => m.developerCount)),
                avgYearsActive: Math.max(...Object.values(performanceMetrics).map(m => m.avgYearsActive)),
                marketPresence: Math.max(...Object.values(performanceMetrics).map(m => m.marketPresence)),
                qualityScore: Math.max(...Object.values(performanceMetrics).map(m => m.qualityScore))
            };
            
            const studioTypes = Object.keys(performanceMetrics).slice(0, 5);
            const datasets = studioTypes.map((studioType, index) => {
                const metrics = performanceMetrics[studioType];
                return {
                    label: studioType,
                    data: [
                        (metrics.avgReplayRate / (maxValues.avgReplayRate || 1)) * 10,
                        (metrics.developerCount / (maxValues.developerCount || 1)) * 10,
                        (metrics.avgYearsActive / (maxValues.avgYearsActive || 1)) * 10,
                        (metrics.marketPresence / (maxValues.marketPresence || 1)) * 10,
                        (metrics.qualityScore / (maxValues.qualityScore || 1)) * 10
                    ],
                    backgroundColor: generateColors(5)[index] + '20',
                    borderColor: generateColors(5)[index],
                    borderWidth: 3,
                    pointBackgroundColor: generateColors(5)[index],
                    pointBorderColor: '#f8f8f2',
                    pointBorderWidth: 2,
                    pointRadius: 6
                };
            });
            
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: [
                        'Replay Rate',
                        'Developer Count',
                        'Experience',
                        'Market Reach',
                        'Quality Score'
                    ],
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 2500,
                        easing: 'easeInOutQuart'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: '📊 Developer Performance Metrics',
                            color: '#bd93f9',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#f8f8f2',
                                font: { size: 11 },
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }
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
                                color: '#f8f8f2',
                                font: { size: 10 },
                                stepSize: 2
                            },
                            grid: { color: '#44475a' },
                            pointLabels: {
                                color: '#f8f8f2',
                                font: { size: 11, weight: 'bold' }
                            }
                        }
                    }
                }
            });
            console.log('Developer Performance Metrics initialized successfully');
        } catch (error) {
            console.error('Error initializing Developer Performance Metrics:', error);
        }
    } else {
        console.log('Insufficient data for Developer Performance Metrics radar chart');
    }

    console.log('Tactical dashboard charts initialization completed');
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

// Initialize Tactical Dashboard Charts (Developer Performance)
function initializeTacticalCharts() {
    console.log('Setting up Developer Performance charts...');
    console.log('Available data:', {
        tacticalSankeyData: typeof tacticalSankeyData !== 'undefined' ? tacticalSankeyData?.length : 'undefined',
        tacticalVennData: typeof tacticalVennData !== 'undefined' ? tacticalVennData?.length : 'undefined',
        tacticalChordData: typeof tacticalChordData !== 'undefined' ? tacticalChordData?.length : 'undefined',
        tacticalDumbbellData: typeof tacticalDumbbellData !== 'undefined' ? tacticalDumbbellData?.length : 'undefined',
        tacticalMarimekkoData: typeof tacticalMarimekkoData !== 'undefined' ? tacticalMarimekkoData?.length : 'undefined'
    });
    
    try {
        // Chart 1: Studio Type Performance - Slope Chart
        initializeDeveloperSlopeChart();
        
        // Chart 2: Geographic Distribution - Clustered Dumbbell Chart
        initializeDeveloperDumbbellChart();
        
        // Chart 3: Developer Maturity Analysis - Enhanced Scatter Plot
        initializeDeveloperMaturityChart();
        
        // Chart 4: Country × Studio Type - Matrix Heatmap
        initializeDeveloperHeatmapChart();
        
        // Chart 5: Developer Performance Radar - Interactive Spider Chart
        initializeDeveloperRadarChart();
        
        // Chart 6: Developer Replay Curve - Line Chart with Studio Type Colors
        initializeDeveloperReplayCurve();
        
        console.log('Developer Performance charts initialized');
    } catch (error) {
        console.error('Error initializing tactical charts:', error);
    }
}

// Chart 1: Studio Type Performance - Slope Chart
function initializeDeveloperSlopeChart() {
    const canvas = document.getElementById('tacticalSankeyChart');
    if (!canvas) {
        console.warn('Canvas tacticalSankeyChart not found');
        return;
    }

    const ctx = canvas.getContext('2d');
    
    // Use available data or create default data
    let chartData = [];
    if (typeof tacticalSankeyData !== 'undefined' && tacticalSankeyData && tacticalSankeyData.length > 0) {
        chartData = tacticalSankeyData;
    } else {
        // Default data for demonstration
        chartData = [
            { studio_type: 'AAA', avg_replay_rate: 0.75, years_active: 25, developer_count: 150 },
            { studio_type: 'Mid-tier', avg_replay_rate: 0.68, years_active: 18, developer_count: 85 },
            { studio_type: 'Indie', avg_replay_rate: 0.62, years_active: 12, developer_count: 45 },
            { studio_type: 'Mobile', avg_replay_rate: 0.58, years_active: 8, developer_count: 30 },
            { studio_type: 'Legacy', avg_replay_rate: 0.82, years_active: 35, developer_count: 12 }
        ];
    }

    // Process data for slope chart
    const studioTypes = [...new Set(chartData.map(d => d.studio_type))];
    const processedData = studioTypes.map(type => {
        const typeData = chartData.filter(d => d.studio_type === type);
        const avgReplayRate = typeData.reduce((sum, d) => sum + (d.avg_replay_rate || 0), 0) / typeData.length;
        const avgYearsActive = typeData.reduce((sum, d) => sum + (d.years_active || 0), 0) / typeData.length;
        const devCount = typeData.reduce((sum, d) => sum + (d.developer_count || 0), 0);
        
        return {
            label: type,
            replayRate: avgReplayRate,
            yearsActive: avgYearsActive,
            count: devCount,
            color: getStudioTypeColor(type)
        };
    }).sort((a, b) => a.yearsActive - b.yearsActive);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: processedData.map(d => `${d.yearsActive.toFixed(1)} years`),
            datasets: [{
                label: 'Studio Performance Trajectory',
                data: processedData.map(d => ({
                    x: d.yearsActive,
                    y: d.replayRate,
                    studio: d.label,
                    count: d.count
                })),
                backgroundColor: processedData.map(d => d.color + '80'),
                borderColor: processedData.map(d => d.color),
                borderWidth: 3,
                pointRadius: processedData.map(d => Math.sqrt(d.count) * 0.3 + 8),
                pointHoverRadius: processedData.map(d => Math.sqrt(d.count) * 0.3 + 12),
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '📊 Studio Performance Trajectory: Experience vs Player Retention',
                    color: '#bd93f9',
                    font: { size: 16, weight: 'bold' }
                },
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(40, 42, 54, 0.95)',
                    titleColor: '#f8f8f2',
                    bodyColor: '#f8f8f2',
                    borderColor: '#bd93f9',
                    borderWidth: 2,
                    callbacks: {
                        title: function(context) {
                            const point = context[0].raw;
                            return `${point.studio} Studios`;
                        },
                        label: function(context) {
                            const point = context.raw;
                            return [
                                `Replay Rate: ${(point.y * 100).toFixed(1)}%`,
                                `Years Active: ${point.x.toFixed(1)}`,
                                `Developer Count: ${point.count}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Average Years Active' },
                    grid: { color: '#44475a' },
                    ticks: { color: '#f8f8f2' }
                },
                y: {
                    title: { display: true, text: 'Average Replay Rate' },
                    grid: { color: '#44475a' },
                    ticks: { color: '#f8f8f2' }
                }
            }
        }
    });
}

// Chart 2: Geographic Distribution - Clustered Dumbbell Chart
function initializeDeveloperDumbbellChart() {
    const canvas = document.getElementById('tacticalVennChart');
    if (!canvas) {
        console.warn('Canvas tacticalVennChart not found');
        return;
    }

    const ctx = canvas.getContext('2d');
    
    // Use available data or create default data
    let chartData = [];
    if (typeof tacticalVennData !== 'undefined' && tacticalVennData && tacticalVennData.length > 0) {
        chartData = tacticalVennData;
    } else {
        // Default data for demonstration
        chartData = [
            { country: 'United States', developer_count: 850, avg_replay_rate: 0.72 },
            { country: 'Finland', developer_count: 650, avg_replay_rate: 0.78 },
            { country: 'United Kingdom', developer_count: 620, avg_replay_rate: 0.69 },
            { country: 'Canada', developer_count: 580, avg_replay_rate: 0.71 },
            { country: 'Sweden', developer_count: 540, avg_replay_rate: 0.76 },
            { country: 'Japan', developer_count: 320, avg_replay_rate: 0.74 },
            { country: 'Germany', developer_count: 280, avg_replay_rate: 0.67 },
            { country: 'France', developer_count: 240, avg_replay_rate: 0.65 }
        ];
    }

    // Process data for dumbbell chart
    const countryData = {};
    chartData.forEach(d => {
        const country = d.country || 'Unknown';
        if (!countryData[country]) {
            countryData[country] = { devCount: 0, replayRates: [] };
        }
        countryData[country].devCount += d.developer_count || 0;
        if (d.avg_replay_rate) {
            countryData[country].replayRates.push(d.avg_replay_rate);
        }
    });

    const processedData = Object.entries(countryData)
        .map(([country, data]) => ({
            country,
            devCount: data.devCount,
            avgReplayRate: data.replayRates.length > 0 
                ? data.replayRates.reduce((a, b) => a + b, 0) / data.replayRates.length 
                : 0
        }))
        .sort((a, b) => b.devCount - a.devCount)
        .slice(0, 8); // Top 8 countries

    // Normalize values for visualization
    const maxDevCount = Math.max(...processedData.map(d => d.devCount));
    const maxReplayRate = Math.max(...processedData.map(d => d.avgReplayRate));

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Developer Count',
                    data: processedData.map((d, i) => ({
                        x: 0,
                        y: i,
                        value: d.devCount,
                        country: d.country,
                        type: 'count'
                    })),
                    backgroundColor: '#4ecdc4',
                    borderColor: '#4ecdc4',
                    pointRadius: processedData.map(d => (d.devCount / maxDevCount) * 15 + 8),
                    pointHoverRadius: processedData.map(d => (d.devCount / maxDevCount) * 15 + 12)
                },
                {
                    label: 'Avg Replay Rate',
                    data: processedData.map((d, i) => ({
                        x: 1,
                        y: i,
                        value: d.avgReplayRate,
                        country: d.country,
                        type: 'replay'
                    })),
                    backgroundColor: '#ff6b6b',
                    borderColor: '#ff6b6b',
                    pointRadius: processedData.map(d => (d.avgReplayRate / maxReplayRate) * 15 + 8),
                    pointHoverRadius: processedData.map(d => (d.avgReplayRate / maxReplayRate) * 15 + 12)
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '🌍 Geographic Performance: Developer Count vs Replay Quality',
                    color: '#bd93f9',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    labels: { color: '#f8f8f2' }
                },
                tooltip: {
                    backgroundColor: 'rgba(40, 42, 54, 0.95)',
                    titleColor: '#f8f8f2',
                    bodyColor: '#f8f8f2',
                    borderColor: '#bd93f9',
                    borderWidth: 2,
                    callbacks: {
                        title: function(context) {
                            return context[0].raw.country;
                        },
                        label: function(context) {
                            const point = context.raw;
                            if (point.type === 'count') {
                                return `Developer Count: ${point.value}`;
                            } else {
                                return `Avg Replay Rate: ${(point.value * 100).toFixed(1)}%`;
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    min: -0.5,
                    max: 1.5,
                    ticks: {
                        stepSize: 1,
                        color: '#f8f8f2',
                        callback: function(value) {
                            return value === 0 ? 'Dev Count' : value === 1 ? 'Replay Rate' : '';
                        }
                    },
                    grid: { display: false }
                },
                y: {
                    type: 'linear',
                    min: -0.5,
                    max: processedData.length - 0.5,
                    ticks: {
                        stepSize: 1,
                        color: '#f8f8f2',
                        callback: function(value) {
                            return processedData[value]?.country || '';
                        }
                    },
                    grid: { color: '#44475a' }
                }
            }
        }
    });
}

// Chart 3: Developer Maturity Analysis - Enhanced Scatter Plot
function initializeDeveloperMaturityChart() {
    const canvas = document.getElementById('tacticalChordChart');
    if (!canvas) {
        console.warn('Canvas tacticalChordChart not found');
        return;
    }

    const ctx = canvas.getContext('2d');
    
    // Use available data or create default data
    let chartData = [];
    if (typeof tacticalChordData !== 'undefined' && tacticalChordData && tacticalChordData.length > 0) {
        chartData = tacticalChordData.slice(0, 100); // Limit for performance
    } else {
        // Default data for demonstration
        chartData = [
            { name: 'Nintendo', maturity_level: 'Veteran', years_active: 45, replay_rate: 0.85, studio_type: 'AAA' },
            { name: 'Sony Interactive', maturity_level: 'Veteran', years_active: 35, replay_rate: 0.78, studio_type: 'AAA' },
            { name: 'Activision', maturity_level: 'Veteran', years_active: 42, replay_rate: 0.72, studio_type: 'AAA' },
            { name: 'Ubisoft', maturity_level: 'Established', years_active: 28, replay_rate: 0.69, studio_type: 'AAA' },
            { name: 'Epic Games', maturity_level: 'Established', years_active: 22, replay_rate: 0.74, studio_type: 'Mid-tier' },
            { name: 'Supercell', maturity_level: 'Established', years_active: 15, replay_rate: 0.81, studio_type: 'Mobile' },
            { name: 'Team Cherry', maturity_level: 'Emerging', years_active: 8, replay_rate: 0.88, studio_type: 'Indie' },
            { name: 'Hades Dev', maturity_level: 'Emerging', years_active: 12, replay_rate: 0.92, studio_type: 'Indie' },
            { name: 'Among Us Dev', maturity_level: 'Emerging', years_active: 6, replay_rate: 0.76, studio_type: 'Indie' }
        ];
    }

    // Process data by maturity level
    const maturityLevels = ['Emerging', 'Established', 'Veteran'];
    const datasets = maturityLevels.map(level => {
        const levelData = chartData.filter(d => d.maturity_level === level);
        return {
            label: level,
            data: levelData.map(d => ({
                x: d.years_active || 0,
                y: d.replay_rate || 0,
                name: d.name || 'Unknown',
                studio_type: d.studio_type || 'Unknown'
            })),
            backgroundColor: getMaturityColor(level) + '60',
            borderColor: getMaturityColor(level),
            borderWidth: 2,
            pointRadius: 8,
            pointHoverRadius: 12
        };
    });

    new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '🧭 Developer Maturity vs Performance Analysis',
                    color: '#bd93f9',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    labels: { color: '#f8f8f2' }
                },
                tooltip: {
                    backgroundColor: 'rgba(40, 42, 54, 0.95)',
                    titleColor: '#f8f8f2',
                    bodyColor: '#f8f8f2',
                    borderColor: '#bd93f9',
                    borderWidth: 2,
                    callbacks: {
                        title: function(context) {
                            return context[0].raw.name;
                        },
                        label: function(context) {
                            const point = context.raw;
                            return [
                                `Maturity: ${context.dataset.label}`,
                                `Years Active: ${point.x}`,
                                `Replay Rate: ${(point.y * 100).toFixed(1)}%`,
                                `Studio Type: ${point.studio_type}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Years Active' },
                    grid: { color: '#44475a' },
                    ticks: { color: '#f8f8f2' }
                },
                y: {
                    title: { display: true, text: 'Replay Rate' },
                    grid: { color: '#44475a' },
                    ticks: { color: '#f8f8f2' }
                }
            }
        }
    });
}

// Chart 4: Country × Studio Type - Matrix Heatmap
function initializeDeveloperHeatmapChart() {
    const canvas = document.getElementById('tacticalDumbbellChart');
    if (!canvas) {
        console.warn('Canvas tacticalDumbbellChart not found');
        return;
    }

    const ctx = canvas.getContext('2d');
    
    // Use available data or create default data
    let chartData = [];
    if (typeof tacticalMarimekkoData !== 'undefined' && tacticalMarimekkoData && tacticalMarimekkoData.length > 0) {
        chartData = tacticalMarimekkoData;
    } else {
        // Default data for demonstration
        const countries = ['United States', 'Finland', 'United Kingdom', 'Canada', 'Sweden', 'Japan'];
        const studioTypes = ['Indie', 'Mobile', 'Mid-tier', 'AAA', 'Legacy'];
        chartData = [];
        countries.forEach(country => {
            studioTypes.forEach(studioType => {
                chartData.push({
                    country,
                    studio_type: studioType,
                    developer_count: Math.floor(Math.random() * 200) + 10,
                    avg_replay_rate: 0.5 + Math.random() * 0.4
                });
            });
        });
    }

    // Create matrix data
    const countries = [...new Set(chartData.map(d => d.country))].slice(0, 6);
    const studioTypes = ['Indie', 'Mobile', 'Mid-tier', 'AAA', 'Legacy'];
    
    const matrixData = [];
    countries.forEach((country, countryIndex) => {
        studioTypes.forEach((studioType, studioIndex) => {
            const dataPoint = chartData.find(d => 
                d.country === country && d.studio_type === studioType
            );
            
            matrixData.push({
                x: studioIndex,
                y: countryIndex,
                v: dataPoint ? dataPoint.developer_count || 0 : 0,
                country,
                studioType,
                replayRate: dataPoint ? dataPoint.avg_replay_rate || 0 : 0
            });
        });
    });

    const maxValue = Math.max(...matrixData.map(d => d.v));

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Developer Count',
                data: matrixData,
                backgroundColor: function(context) {
                    const value = context.raw.v;
                    const intensity = value / maxValue;
                    return `rgba(52, 152, 219, ${intensity})`;
                },
                borderColor: '#2980b9',
                borderWidth: 1,
                pointRadius: function(context) {
                    const value = context.raw.v;
                    return Math.sqrt(value) * 0.5 + 5;
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '🛠 Country × Studio Type Matrix Heatmap',
                    color: '#bd93f9',
                    font: { size: 16, weight: 'bold' }
                },
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(40, 42, 54, 0.95)',
                    titleColor: '#f8f8f2',
                    bodyColor: '#f8f8f2',
                    borderColor: '#bd93f9',
                    borderWidth: 2,
                    callbacks: {
                        title: function(context) {
                            const point = context[0].raw;
                            return `${point.country} - ${point.studioType}`;
                        },
                        label: function(context) {
                            const point = context.raw;
                            return [
                                `Developer Count: ${point.v}`,
                                `Avg Replay Rate: ${(point.replayRate * 100).toFixed(1)}%`
                            ];
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
                        color: '#f8f8f2',
                        callback: function(value) {
                            return studioTypes[value] || '';
                        }
                    },
                    title: { display: true, text: 'Studio Type', color: '#f8f8f2' }
                },
                y: {
                    type: 'linear',
                    min: -0.5,
                    max: countries.length - 0.5,
                    ticks: {
                        stepSize: 1,
                        color: '#f8f8f2',
                        callback: function(value) {
                            return countries[value] || '';
                        }
                    },
                    title: { display: true, text: 'Country', color: '#f8f8f2' }
                }
            }
        }
    });
}

// Chart 5: Developer Performance Radar - Interactive Spider Chart
function initializeDeveloperRadarChart() {
    const canvas = document.getElementById('tacticalMarimekkoChart');
    if (!canvas) {
        console.warn('Canvas tacticalMarimekkoChart not found');
        return;
    }

    const ctx = canvas.getContext('2d');
    
    // Use available data or create default data
    let chartData = [];
    if (typeof tacticalDumbbellData !== 'undefined' && tacticalDumbbellData && tacticalDumbbellData.length > 0) {
        chartData = tacticalDumbbellData;
    } else {
        // Default data for demonstration
        chartData = [
            { studio_type: 'AAA', avg_replay_rate: 0.75, years_active: 25, developer_count: 150 },
            { studio_type: 'Mid-tier', avg_replay_rate: 0.68, years_active: 18, developer_count: 85 },
            { studio_type: 'Indie', avg_replay_rate: 0.62, years_active: 12, developer_count: 45 },
            { studio_type: 'Mobile', avg_replay_rate: 0.58, years_active: 8, developer_count: 30 },
            { studio_type: 'Legacy', avg_replay_rate: 0.82, years_active: 35, developer_count: 12 }
        ];
    }

    // Calculate metrics by studio type
    const studioTypes = [...new Set(chartData.map(d => d.studio_type))];
    const datasets = studioTypes.map(type => {
        const typeData = chartData.filter(d => d.studio_type === type);
        
        // Calculate normalized metrics (0-100 scale)
        const avgReplayRate = typeData.reduce((sum, d) => sum + (d.avg_replay_rate || 0), 0) / typeData.length * 100;
        const avgYearsActive = Math.min(typeData.reduce((sum, d) => sum + (d.years_active || 0), 0) / typeData.length * 2, 100);
        const devCount = Math.min(typeData.reduce((sum, d) => sum + (d.developer_count || 0), 0) / 10, 100);
        const marketReach = Math.min(typeData.length * 20, 100); // Based on data points
        const consistency = Math.min(avgReplayRate * 1.2, 100); // Replay rate as consistency indicator
        
        return {
            label: type,
            data: [avgReplayRate, avgYearsActive, devCount, marketReach, consistency],
            backgroundColor: getStudioTypeColor(type) + '20',
            borderColor: getStudioTypeColor(type),
            borderWidth: 2,
            pointBackgroundColor: getStudioTypeColor(type),
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: getStudioTypeColor(type)
        };
    });

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Player Retention', 'Experience', 'Scale', 'Market Reach', 'Consistency'],
            datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '🎮 Developer Performance Radar by Studio Type',
                    color: '#bd93f9',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    labels: { color: '#f8f8f2' }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: '#f8f8f2'
                    },
                    grid: {
                        color: '#44475a'
                    },
                    pointLabels: {
                        color: '#f8f8f2'
                    }
                }
            }
        }
    });
}

// Chart 6: Developer Replay Curve - Line Chart with Studio Type Colors
function initializeDeveloperReplayCurve() {
    const canvas = document.getElementById('tacticalFocusChart');
    if (!canvas) {
        console.warn('Canvas tacticalFocusChart not found');
        return;
    }

    const ctx = canvas.getContext('2d');
    
    // Use available data or create default data
    let chartData = [];
    if (typeof tacticalChordData !== 'undefined' && tacticalChordData && tacticalChordData.length > 0) {
        chartData = tacticalChordData;
    } else {
        // Default data for demonstration
        chartData = [
            { studio_type: 'AAA', years_active: 5, replay_rate: 0.65 },
            { studio_type: 'AAA', years_active: 15, replay_rate: 0.72 },
            { studio_type: 'AAA', years_active: 25, replay_rate: 0.75 },
            { studio_type: 'AAA', years_active: 35, replay_rate: 0.78 },
            { studio_type: 'Indie', years_active: 2, replay_rate: 0.58 },
            { studio_type: 'Indie', years_active: 8, replay_rate: 0.62 },
            { studio_type: 'Indie', years_active: 15, replay_rate: 0.68 },
            { studio_type: 'Mobile', years_active: 3, replay_rate: 0.55 },
            { studio_type: 'Mobile', years_active: 8, replay_rate: 0.58 },
            { studio_type: 'Mobile', years_active: 12, replay_rate: 0.61 }
        ];
    }

    // Group data by studio type and create trend lines
    const studioTypes = [...new Set(chartData.map(d => d.studio_type))];
    const datasets = studioTypes.map(type => {
        const typeData = chartData
            .filter(d => d.studio_type === type)
            .sort((a, b) => (a.years_active || 0) - (b.years_active || 0));
        
        // Create moving average for smoother curve
        const smoothedData = [];
        const windowSize = Math.max(1, Math.floor(typeData.length / 5));
        
        for (let i = 0; i < typeData.length; i += windowSize) {
            const window = typeData.slice(i, i + windowSize);
            const avgYears = window.reduce((sum, d) => sum + (d.years_active || 0), 0) / window.length;
            const avgReplay = window.reduce((sum, d) => sum + (d.replay_rate || 0), 0) / window.length;
            
            smoothedData.push({
                x: avgYears,
                y: avgReplay
            });
        }
        
        return {
            label: type,
            data: smoothedData,
            borderColor: getStudioTypeColor(type),
            backgroundColor: getStudioTypeColor(type) + '20',
            borderWidth: 3,
            fill: false,
            tension: 0.4,
            pointRadius: 6,
            pointHoverRadius: 10
        };
    });

    new Chart(ctx, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '🔁 Developer Replay Rate Evolution Over Time',
                    color: '#bd93f9',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    labels: { color: '#f8f8f2' }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    title: { display: true, text: 'Years Active' },
                    grid: { color: '#44475a' },
                    ticks: { color: '#f8f8f2' }
                },
                y: {
                    title: { display: true, text: 'Replay Rate' },
                    grid: { color: '#44475a' },
                    ticks: { color: '#f8f8f2' }
                }
            }
        }
    });
}

// Helper functions for colors
function getStudioTypeColor(type) {
    const colors = {
        'AAA': '#e74c3c',
        'Mid-tier': '#f39c12',
        'Indie': '#3498db',
        'Mobile': '#9b59b6',
        'Legacy': '#2ecc71'
    };
    return colors[type] || '#95a5a6';
}

function getMaturityColor(level) {
    const colors = {
        'Emerging': '#3498db',
        'Established': '#f39c12',
        'Veteran': '#e74c3c'
    };
    return colors[level] || '#95a5a6';
}

// Lifecycle Dashboard Charts
function initializeLifecycleCharts() {
    console.log('Initializing lifecycle charts...');
    // Lifecycle chart implementations would go here
}

// Evolution Dashboard Charts  
function initializeEvolutionCharts() {
    console.log('Initializing evolution charts...');
    // Evolution chart implementations would go here
} 