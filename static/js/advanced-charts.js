// Advanced Charts for Tactical, Lifecycle, and Evolution Dashboards

// Enhanced Tactical Dashboard Charts with Advanced Visualizations
function initializeTacticalCharts() {
    console.log('Initializing enhanced tactical dashboard charts...');
    console.log('Tactical data available:', {
        sankey: tacticalSankeyData?.length || 0,
        venn: tacticalVennData?.length || 0,
        chord: tacticalChordData?.length || 0,
        dumbbell: tacticalDumbbellData?.length || 0,
        marimekko: tacticalMarimekkoData?.length || 0
    });
    
    // 1. Platform Strategy Map (Sunburst/Hive Chart) - Genre → Platform → Publisher Flow
    if (tacticalSankeyData && tacticalSankeyData.length > 0) {
        console.log('Initializing Platform Strategy Map...');
        const sankeyCtx = document.getElementById('tacticalSankeyChart');
        if (!sankeyCtx) {
            console.error('tacticalSankeyChart canvas not found');
            return;
        }
        
        try {
            const ctx = sankeyCtx.getContext('2d');
            
            // Process data for sunburst-style visualization
            const genreThemeMap = {
                'Action': 'Combat & Adventure',
                'Adventure': 'Exploration & Story',
                'Role-Playing': 'Character Development',
                'Strategy': 'Tactical Thinking',
                'Simulation': 'Real-World Modeling',
                'Sports': 'Athletic Competition',
                'Racing': 'Speed & Competition',
                'Shooter': 'Combat & Precision',
                'Puzzle': 'Logic & Problem Solving',
                'Platform': 'Movement & Agility'
            };
            
            // Create hierarchical data structure
            const themeData = {};
            tacticalSankeyData.forEach(item => {
                const theme = genreThemeMap[item.genre] || 'Other Themes';
                if (!themeData[theme]) {
                    themeData[theme] = { total: 0, platforms: {} };
                }
                themeData[theme].total += item.count;
                
                if (!themeData[theme].platforms[item.platform]) {
                    themeData[theme].platforms[item.platform] = 0;
                }
                themeData[theme].platforms[item.platform] += item.count;
            });
            
            // Create multi-level donut chart to simulate sunburst
            const themes = Object.keys(themeData).slice(0, 6);
            const innerData = themes.map(theme => themeData[theme].total);
            const outerData = [];
            const outerLabels = [];
            
            themes.forEach(theme => {
                const platforms = Object.keys(themeData[theme].platforms).slice(0, 3);
                platforms.forEach(platform => {
                    outerData.push(themeData[theme].platforms[platform]);
                    outerLabels.push(`${platform.substring(0, 8)}...`);
                });
            });
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: themes,
                    datasets: [
                        {
                            label: 'Theme Distribution',
                            data: innerData,
                            backgroundColor: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'],
                            borderColor: '#282a36',
                            borderWidth: 3,
                            radius: '40%',
                            cutout: '20%'
                        },
                        {
                            label: 'Platform Distribution',
                            data: outerData,
                            backgroundColor: outerData.map((_, i) => {
                                const colors = ['#ff6b6b80', '#4ecdc480', '#45b7d180', '#96ceb480', '#feca5780', '#ff9ff380'];
                                return colors[Math.floor(i / 3) % colors.length];
                            }),
                            borderColor: '#282a36',
                            borderWidth: 2,
                            radius: '80%',
                            cutout: '50%'
                        }
                    ]
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
                            text: '🎯 Platform Strategy Map (Theme → Platform)',
                            color: '#bd93f9',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            position: 'right',
                            labels: {
                                color: '#f8f8f2',
                                font: { size: 10 },
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
                            cornerRadius: 10,
                            callbacks: {
                                title: function(context) {
                                    return context[0].label;
                                },
                                label: function(context) {
                                    const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
                                    const percentage = ((context.parsed / total) * 100).toFixed(1);
                                    return [
                                        `Games: ${context.parsed}`,
                                        `Market Share: ${percentage}%`,
                                        `Strategy: ${context.datasetIndex === 0 ? 'Theme Focus' : 'Platform Reach'}`
                                    ];
                                }
                            }
                        }
                    }
                }
            });
            console.log('Platform Strategy Map initialized successfully');
        } catch (error) {
            console.error('Error initializing Platform Strategy Map:', error);
        }
    }

    // 2. Cross-Platform Footprint (UpSet Plot Style) - Platform Overlap Analysis
    if (tacticalVennData && tacticalVennData.length > 0) {
        console.log('Initializing Cross-Platform Footprint Analysis...');
        const vennCtx = document.getElementById('tacticalVennChart');
        if (!vennCtx) {
            console.error('tacticalVennChart canvas not found');
            return;
        }
        
        try {
            const ctx = vennCtx.getContext('2d');
            
            // Create UpSet plot style visualization using stacked bars
            const platformCombinations = tacticalVennData.slice(0, 10);
            
            // Create proper labels with platform count information
            const labels = platformCombinations.map(item => {
                if (item.platform_count === 1) {
                    return 'Exclusive';
                } else {
                    return `${item.platform_count} Platforms`;
                }
            });
            
            // Create intersection matrix visualization
            const exclusiveGames = platformCombinations.map(item => item.platform_count === 1 ? item.game_count : 0);
            const multiPlatformGames = platformCombinations.map(item => item.platform_count > 1 ? item.game_count : 0);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Exclusive Games',
                            data: exclusiveGames,
                            backgroundColor: '#ff6b6b80',
                            borderColor: '#ff6b6b',
                            borderWidth: 2,
                            borderRadius: 6
                        },
                        {
                            label: 'Multi-Platform Games',
                            data: multiPlatformGames,
                            backgroundColor: '#4ecdc480',
                            borderColor: '#4ecdc4',
                            borderWidth: 2,
                            borderRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutCubic'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: '📊 Cross-Platform Footprint Analysis',
                            color: '#bd93f9',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            position: 'top',
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
                                    const item = platformCombinations[context[0].dataIndex];
                                    return `${item.platform_count} Platform Coverage`;
                                },
                                label: function(context) {
                                    const item = platformCombinations[context.dataIndex];
                                    const strategy = item.platform_count === 1 ? 'Platform Exclusive' : 
                                                   item.platform_count <= 3 ? 'Selective Multi-Platform' : 
                                                   'Wide Platform Strategy';
                                    return [
                                        `${context.dataset.label}: ${context.parsed.y} games`,
                                        `Strategy Type: ${strategy}`,
                                        `Market Reach: ${item.platform_count > 3 ? 'Broad' : item.platform_count > 1 ? 'Moderate' : 'Focused'}`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            stacked: true,
                            ticks: { 
                                color: '#f8f8f2',
                                font: { size: 10 }
                            },
                            grid: { color: '#0f3460' }
                        },
                        y: {
                            stacked: true,
                            beginAtZero: true,
                            ticks: { color: '#f8f8f2' },
                            grid: { color: '#0f3460' },
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
            console.log('Cross-Platform Footprint Analysis initialized successfully');
        } catch (error) {
            console.error('Error initializing Cross-Platform Footprint Analysis:', error);
        }
    }

    // 3. Developer-Genre-Platform Flow (Hive/Alluvial Diagram)
    if (tacticalChordData && tacticalChordData.length > 0) {
        console.log('Initializing Developer-Platform Flow Analysis...');
        console.log('Tactical chord data sample:', tacticalChordData.slice(0, 3));
        const chordCtx = document.getElementById('tacticalChordChart');
        if (!chordCtx) {
            console.error('tacticalChordChart canvas not found');
            return;
        }
        
        try {
            const ctx = chordCtx.getContext('2d');
            
            // Limit to top 10 developer-platform combinations for better performance
            const flowData = tacticalChordData
                .filter(item => item.count >= 2) // Only show meaningful connections
                .slice(0, 10);
            console.log('Flow data processed:', flowData.length, 'items');
            
            if (flowData.length === 0) {
                console.warn('No flow data after filtering');
                return;
            }
            
            // Validate data structure
            if (!flowData.every(item => item.developer && item.platform && typeof item.count === 'number')) {
                console.error('Invalid data structure in tacticalChordData');
                return;
            }
            
            // Create simple labels and data
            const labels = flowData.map(item => `${item.developer.substring(0, 12)}... → ${item.platform.substring(0, 10)}...`);
            const data = flowData.map(item => item.count);
            
            console.log('Chart labels:', labels.slice(0, 3));
            console.log('Chart data:', data.slice(0, 3));
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Games Published',
                        data: data,
                        backgroundColor: generateColors(flowData.length).map(color => color + '80'),
                        borderColor: generateColors(flowData.length),
                        borderWidth: 2,
                        borderRadius: 4
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 1500,
                        easing: 'easeInOutCubic'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: '🌊 Developer → Platform Flow Analysis',
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
                                    const item = flowData[context.dataIndex];
                                    return `${item.developer} → ${item.platform}`;
                                },
                                label: function(context) {
                                    const item = flowData[context.dataIndex];
                                    return [
                                        `Games: ${item.count}`,
                                        `Flow Strength: ${item.count > 10 ? 'Strong' : item.count > 3 ? 'Moderate' : 'Weak'}`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: { color: '#f8f8f2' },
                            grid: { color: '#0f3460' },
                            title: {
                                display: true,
                                text: 'Games Published',
                                color: '#50fa7b',
                                font: { size: 12, weight: 'bold' }
                            }
                        },
                        y: {
                            ticks: { 
                                color: '#f8f8f2',
                                font: { size: 9 }
                            },
                            grid: { color: '#0f3460' }
                        }
                    }
                }
            });
            console.log('Developer-Platform Flow Analysis initialized successfully');
        } catch (error) {
            console.error('Error initializing Developer-Platform Flow Analysis:', error);
            // Create a fallback message
            const canvas = document.getElementById('tacticalChordChart');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#f8f8f2';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Chart temporarily unavailable', canvas.width/2, canvas.height/2);
            }
        }
    } else {
        console.log('No tactical chord data available - length:', tacticalChordData ? tacticalChordData.length : 'undefined');
    }

    // 4. Performance Spread (Violin/Box Plot Style) - Rating Distribution Analysis
    if (tacticalDumbbellData && tacticalDumbbellData.length > 0) {
        console.log('Initializing Performance Spread Analysis...');
        const dumbbellCtx = document.getElementById('tacticalDumbbellChart');
        if (!dumbbellCtx) {
            console.error('tacticalDumbbellChart canvas not found');
            return;
        }
        
        try {
            const ctx = dumbbellCtx.getContext('2d');
            
            const performanceData = tacticalDumbbellData.slice(0, 10);
            
            // Create violin plot style using multiple datasets
            const datasets = [
                {
                    label: 'Rating Range (Min-Max)',
                    data: performanceData.map(item => ({
                        x: item.genre.substring(0, 8) + '...',
                        y: item.max_rating - item.min_rating
                    })),
                    backgroundColor: '#ff555580',
                    borderColor: '#ff5555',
                    borderWidth: 3,
                    type: 'bar',
                    borderRadius: 8,
                    order: 2
                },
                {
                    label: 'Average Rating',
                    data: performanceData.map(item => item.avg_rating),
                    backgroundColor: '#50fa7b',
                    borderColor: '#f8f8f2',
                    borderWidth: 3,
                    pointRadius: 8,
                    pointHoverRadius: 12,
                    type: 'line',
                    tension: 0.4,
                    order: 1
                },
                {
                    label: 'Performance Consistency',
                    data: performanceData.map(item => {
                        const consistency = 10 - (item.max_rating - item.min_rating);
                        return Math.max(0, consistency);
                    }),
                    backgroundColor: '#bd93f980',
                    borderColor: '#bd93f9',
                    borderWidth: 2,
                    type: 'bar',
                    borderRadius: 4,
                    order: 3
                }
            ];
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: performanceData.map(item => item.genre.substring(0, 10) + '...'),
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 2500,
                        easing: 'easeInOutElastic'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: '📈 Performance Spread Analysis (Violin Plot Style)',
                            color: '#bd93f9',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            position: 'top',
                            labels: {
                                color: '#f8f8f2',
                                font: { size: 10 },
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
                                    const item = performanceData[context[0].dataIndex];
                                    return `${item.genre} Performance Profile`;
                                },
                                afterTitle: function(context) {
                                    const item = performanceData[context[0].dataIndex];
                                    return `Platform: ${item.platform} | Games: ${item.game_count}`;
                                },
                                label: function(context) {
                                    const item = performanceData[context.dataIndex];
                                    const spread = item.max_rating - item.min_rating;
                                    const consistency = spread < 2 ? 'Very High' : spread < 3 ? 'High' : spread < 4 ? 'Moderate' : 'Low';
                                    
                                    if (context.dataset.label.includes('Range')) {
                                        return [
                                            `Rating Spread: ${spread.toFixed(2)}`,
                                            `Min: ${item.min_rating} | Max: ${item.max_rating}`,
                                            `Consistency: ${consistency}`
                                        ];
                                    } else if (context.dataset.label.includes('Average')) {
                                        return [
                                            `Average Rating: ${item.avg_rating.toFixed(2)}`,
                                            `Quality Tier: ${item.avg_rating >= 8 ? 'Premium' : item.avg_rating >= 7 ? 'High' : item.avg_rating >= 6 ? 'Good' : 'Standard'}`
                                        ];
                                    } else {
                                        return [
                                            `Consistency Score: ${context.parsed.y.toFixed(1)}/10`,
                                            `Predictability: ${consistency}`
                                        ];
                                    }
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { 
                                color: '#f8f8f2',
                                maxRotation: 45,
                                font: { size: 9 }
                            },
                            grid: { color: '#0f3460' }
                        },
                        y: {
                            beginAtZero: true,
                            max: 10,
                            ticks: { color: '#f8f8f2' },
                            grid: { color: '#0f3460' },
                            title: {
                                display: true,
                                text: 'Rating Scale / Performance Metrics',
                                color: '#50fa7b',
                                font: { size: 12, weight: 'bold' }
                            }
                        }
                    }
                }
            });
            console.log('Performance Spread Analysis initialized successfully');
        } catch (error) {
            console.error('Error initializing Performance Spread Analysis:', error);
        }
    }

    // 5. Market Concentration Matrix (Heatmap with Tooltips)
    if (tacticalMarimekkoData && tacticalMarimekkoData.length > 0) {
        console.log('Initializing Market Concentration Matrix...');
        console.log('Tactical marimekko data sample:', tacticalMarimekkoData.slice(0, 3));
        const marimekkoCtx = document.getElementById('tacticalMarimekkoChart');
        if (!marimekkoCtx) {
            console.error('tacticalMarimekkoChart canvas not found');
            return;
        }
        
        try {
            const ctx = marimekkoCtx.getContext('2d');
            
            // Limit to top 15 genre-platform combinations for better performance
            const matrixData = tacticalMarimekkoData
                .filter(item => item.count >= 3) // Only show meaningful combinations
                .slice(0, 15);
            console.log('Matrix data processed:', matrixData.length, 'items');
            
            if (matrixData.length === 0) {
                console.warn('No matrix data after filtering');
                return;
            }
            
            // Validate data structure
            if (!matrixData.every(item => item.genre && item.platform && typeof item.count === 'number')) {
                console.error('Invalid data structure in tacticalMarimekkoData');
                return;
            }
            
            // Create simple visualization
            const labels = matrixData.map(item => `${item.genre.substring(0, 10)}... × ${item.platform.substring(0, 10)}...`);
            const data = matrixData.map(item => item.count);
            
            console.log('Matrix chart labels:', labels.slice(0, 3));
            console.log('Matrix chart data:', data.slice(0, 3));
            
            const backgroundColors = data.map(count => {
                if (count > 50) return '#ff6b6b80';
                if (count > 20) return '#feca5780';
                return '#4ecdc480';
            });
            const borderColors = data.map(count => {
                if (count > 50) return '#ff6b6b';
                if (count > 20) return '#feca57';
                return '#4ecdc4';
            });
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Market Concentration',
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
                        duration: 1500,
                        easing: 'easeInOutQuart'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: '🔥 Market Concentration Matrix (Heatmap)',
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
                                    return `${item.genre} × ${item.platform}`;
                                },
                                label: function(context) {
                                    const item = matrixData[context.dataIndex];
                                    const totalGames = matrixData.reduce((sum, d) => sum + d.count, 0);
                                    const marketShare = ((item.count / totalGames) * 100).toFixed(2);
                                    const intensity = item.count > 50 ? 'High' : item.count > 20 ? 'Medium' : 'Low';
                                    return [
                                        `Games: ${item.count}`,
                                        `Market Share: ${marketShare}%`,
                                        `Concentration: ${intensity}`,
                                        `Strategic Value: ${intensity === 'High' ? 'Prime Market' : intensity === 'Medium' ? 'Growth Opportunity' : 'Niche Market'}`
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
                            grid: { color: '#0f3460' },
                            title: {
                                display: true,
                                text: 'Genre × Platform Combinations',
                                color: '#8be9fd',
                                font: { size: 12, weight: 'bold' }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#f8f8f2' },
                            grid: { color: '#0f3460' },
                            title: {
                                display: true,
                                text: 'Number of Games',
                                color: '#ff79c6',
                                font: { size: 12, weight: 'bold' }
                            }
                        }
                    }
                }
            });
            console.log('Market Concentration Matrix initialized successfully');
        } catch (error) {
            console.error('Error initializing Market Concentration Matrix:', error);
            // Create a fallback message
            const canvas = document.getElementById('tacticalMarimekkoChart');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#f8f8f2';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Chart temporarily unavailable', canvas.width/2, canvas.height/2);
            }
        }
    } else {
        console.log('No tactical marimekko data available - length:', tacticalMarimekkoData ? tacticalMarimekkoData.length : 'undefined');
    }

    // 6. Focus Area Comparison (Radar/Radar Area Chart) - Strategic Analysis
    if (tacticalSankeyData && tacticalDumbbellData && tacticalMarimekkoData) {
        console.log('Initializing Focus Area Comparison...');
        const focusCtx = document.getElementById('tacticalFocusChart');
        if (!focusCtx) {
            console.error('tacticalFocusChart canvas not found');
            return;
        }
        
        try {
            const ctx = focusCtx.getContext('2d');
            
            // Aggregate data for focus area analysis
            const focusAreas = {};
            
            // Process different data sources for comprehensive analysis
            if (tacticalSankeyData.length > 0) {
                tacticalSankeyData.slice(0, 6).forEach(item => {
                    if (!focusAreas[item.genre]) {
                        focusAreas[item.genre] = {
                            marketPresence: 0,
                            platformReach: 0,
                            competitiveIntensity: 0,
                            qualityConsistency: 0,
                            strategicValue: 0
                        };
                    }
                    focusAreas[item.genre].marketPresence += item.count;
                });
            }
            
            if (tacticalDumbbellData.length > 0) {
                tacticalDumbbellData.slice(0, 6).forEach(item => {
                    if (focusAreas[item.genre]) {
                        const consistency = 10 - (item.max_rating - item.min_rating);
                        focusAreas[item.genre].qualityConsistency = Math.max(0, consistency);
                        focusAreas[item.genre].strategicValue = item.avg_rating;
                    }
                });
            }
            
            // Calculate platform reach and competitive intensity
            Object.keys(focusAreas).forEach(genre => {
                const genreData = tacticalMarimekkoData.filter(item => item.genre === genre);
                focusAreas[genre].platformReach = genreData.length;
                focusAreas[genre].competitiveIntensity = genreData.reduce((sum, item) => sum + item.count, 0) / 10;
            });
            
            // Normalize values to 0-10 scale
            const maxValues = {
                marketPresence: Math.max(...Object.values(focusAreas).map(area => area.marketPresence)),
                platformReach: Math.max(...Object.values(focusAreas).map(area => area.platformReach)),
                competitiveIntensity: Math.max(...Object.values(focusAreas).map(area => area.competitiveIntensity)),
                qualityConsistency: 10,
                strategicValue: 10
            };
            
            const focusGenres = Object.keys(focusAreas).slice(0, 5);
            const datasets = focusGenres.map((genre, index) => {
                const area = focusAreas[genre];
                return {
                    label: genre,
                    data: [
                        (area.marketPresence / maxValues.marketPresence) * 10,
                        (area.platformReach / maxValues.platformReach) * 10,
                        Math.min(area.competitiveIntensity / maxValues.competitiveIntensity * 10, 10),
                        area.qualityConsistency,
                        area.strategicValue
                    ],
                    backgroundColor: generateColors(5)[index] + '20',
                    borderColor: generateColors(5)[index],
                    borderWidth: 3,
                    pointBackgroundColor: generateColors(5)[index],
                    pointBorderColor: '#f8f8f2',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                };
            });
            
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: [
                        'Market Presence',
                        'Platform Reach',
                        'Competition Level',
                        'Quality Consistency',
                        'Strategic Value'
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
                            text: '🎯 Focus Area Comparison (Strategic Radar)',
                            color: '#bd93f9',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#f8f8f2',
                                font: { size: 10 },
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
                            cornerRadius: 10,
                            callbacks: {
                                title: function(context) {
                                    return `${focusGenres[context.datasetIndex]} Genre Analysis`;
                                },
                                label: function(context) {
                                    const metrics = [
                                        'Market Presence',
                                        'Platform Reach', 
                                        'Competition Level',
                                        'Quality Consistency',
                                        'Strategic Value'
                                    ];
                                    const value = context.parsed.r;
                                    const rating = value >= 8 ? 'Excellent' : value >= 6 ? 'Good' : value >= 4 ? 'Average' : 'Below Average';
                                    return [
                                        `${metrics[context.dataIndex]}: ${value.toFixed(1)}/10`,
                                        `Rating: ${rating}`,
                                        `Strategic Priority: ${value >= 7 ? 'High' : value >= 5 ? 'Medium' : 'Low'}`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            min: 0,
                            max: 10,
                            ticks: {
                                stepSize: 2,
                                color: '#f8f8f2',
                                backdropColor: 'transparent',
                                font: { size: 10 }
                            },
                            grid: {
                                color: '#0f3460',
                                lineWidth: 2
                            },
                            angleLines: {
                                color: '#0f3460',
                                lineWidth: 1
                            },
                            pointLabels: {
                                color: '#8be9fd',
                                font: { size: 11, weight: 'bold' }
                            }
                        }
                    }
                }
            });
            console.log('Focus Area Comparison initialized successfully');
        } catch (error) {
            console.error('Error initializing Focus Area Comparison:', error);
        }
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