// Data initialization script - receives data from Flask template
function initializeData(dataFromServer) {
    console.log('Starting data initialization...');
    console.log('Raw data from server:', dataFromServer);
    
    try {
        // Assign data to global variables for use in charts
        stats = dataFromServer.stats;
        topGames = dataFromServer.topGames;
        platformCounts = dataFromServer.platformCounts;
        genreCounts = dataFromServer.genreCounts;
        gamesPerYear = dataFromServer.gamesPerYear;
        publisherCounts = dataFromServer.publisherCounts;
        avgRatingPlatform = dataFromServer.avgRatingPlatform;
        avgRatingDeveloper = dataFromServer.avgRatingDeveloper;
        
        // Enhanced analytics data
        directorAnalytics = dataFromServer.directorAnalytics;
        gameTypeDistribution = dataFromServer.gameTypeDistribution;
        ratingDistribution = dataFromServer.ratingDistribution;
        votesAnalytics = dataFromServer.votesAnalytics;
        mostVotedGames = dataFromServer.mostVotedGames;
        collectionSummary = dataFromServer.collectionSummary;
        
        // Operational dashboard data
        recentReleases = dataFromServer.recentReleases;
        ratingTrends = dataFromServer.ratingTrends;
        monthlyActivity = dataFromServer.monthlyActivity;
        platformPerformance = dataFromServer.platformPerformance;
        topRatedRecent = dataFromServer.topRatedRecent;
        
        // Tactical dashboard data
        tacticalSankeyData = dataFromServer.tacticalSankeyData;
        tacticalVennData = dataFromServer.tacticalVennData;
        tacticalChordData = dataFromServer.tacticalChordData;
        tacticalDumbbellData = dataFromServer.tacticalDumbbellData;
        tacticalMarimekkoData = dataFromServer.tacticalMarimekkoData;
        tacticalDeveloperProfiles = dataFromServer.tacticalDeveloperProfiles;
        
        console.log('=== TACTICAL DATA DEBUG ===');
        console.log('tacticalSankeyData:', tacticalSankeyData);
        console.log('tacticalVennData:', tacticalVennData);
        console.log('tacticalChordData:', tacticalChordData);
        console.log('tacticalDumbbellData:', tacticalDumbbellData);
        console.log('tacticalMarimekkoData:', tacticalMarimekkoData);
        console.log('tacticalDeveloperProfiles:', tacticalDeveloperProfiles);
        
        // Use real tactical matrix data from server
        tacticalMatrixData = dataFromServer.tacticalMatrixData || [];
        
        console.log('Real tactical matrix data from server:', tacticalMatrixData);
        
        // If no real data, create enhanced sample data
        if (!tacticalMatrixData || tacticalMatrixData.length === 0) {
            console.log('No real matrix data, creating enhanced sample data');
            const countries = [
                { name: 'United States', devs: 850, strength: 0.85 },
                { name: 'Japan', devs: 420, strength: 0.90 },
                { name: 'United Kingdom', devs: 320, strength: 0.78 },
                { name: 'Canada', devs: 280, strength: 0.75 },
                { name: 'Germany', devs: 240, strength: 0.72 },
                { name: 'France', devs: 180, strength: 0.70 },
                { name: 'Sweden', devs: 160, strength: 0.82 },
                { name: 'Finland', devs: 120, strength: 0.85 },
                { name: 'South Korea', devs: 200, strength: 0.77 },
                { name: 'China', devs: 300, strength: 0.68 }
            ];
            
            const studioTypes = [
                { type: 'AAA', weight: 0.15, quality: 0.85 },
                { type: 'Mid-tier', weight: 0.25, quality: 0.75 },
                { type: 'Indie', weight: 0.35, quality: 0.65 },
                { type: 'Mobile', weight: 0.20, quality: 0.60 },
                { type: 'Legacy', weight: 0.05, quality: 0.70 }
            ];
            
            tacticalMatrixData = [];
            countries.forEach(country => {
                studioTypes.forEach(studio => {
                    const developerCount = Math.floor(country.devs * studio.weight * (0.8 + Math.random() * 0.4));
                    const replayRate = (country.strength * studio.quality) * (0.9 + Math.random() * 0.2);
                    
                    if (developerCount > 0) {
                        tacticalMatrixData.push({
                            country: country.name,
                            studio_type: studio.type,
                            developer_count: developerCount,
                            avg_replay_rate: Math.min(1.0, replayRate)
                        });
                    }
                });
            });
        }
        
        console.log('Final tactical matrix data:', tacticalMatrixData);
        
        // Set global variable for chart access
        window.tacticalMatrixData = tacticalMatrixData;
        
        // Lifecycle dashboard data
        lifecycleSurvivalData = dataFromServer.lifecycleSurvivalData;
        lifecycleRidgelineData = dataFromServer.lifecycleRidgelineData;
        lifecycleTimelineData = dataFromServer.lifecycleTimelineData;
        lifecycleHexbinData = dataFromServer.lifecycleHexbinData;
        lifecycleParallelData = dataFromServer.lifecycleParallelData;
        
        // Evolution dashboard data
        evolutionStreamData = dataFromServer.evolutionStreamData;
        evolutionBubbleData = dataFromServer.evolutionBubbleData;
        evolutionHexbinData = dataFromServer.evolutionHexbinData;
        evolutionParallelData = dataFromServer.evolutionParallelData;
        evolutionTreeData = dataFromServer.evolutionTreeData;
        
        // Debug logging
        console.log('Data initialized successfully:', {
            stats: stats,
            platformCounts: platformCounts?.length || 0,
            genreCounts: genreCounts?.length || 0,
            gamesPerYear: gamesPerYear?.length || 0,
            publisherCounts: publisherCounts?.length || 0,
            operationalData: {
                recentReleases: recentReleases?.length || 0,
                ratingTrends: ratingTrends?.length || 0,
                monthlyActivity: monthlyActivity?.length || 0,
                platformPerformance: platformPerformance?.length || 0,
                topRatedRecent: topRatedRecent?.length || 0
            },
            tacticalData: {
                sankey: tacticalSankeyData?.length || 0,
                venn: tacticalVennData?.length || 0,
                chord: tacticalChordData?.length || 0,
                dumbbell: tacticalDumbbellData?.length || 0,
                marimekko: tacticalMarimekkoData?.length || 0,
                developerProfiles: tacticalDeveloperProfiles?.length || 0
            },
            lifecycleData: {
                survival: lifecycleSurvivalData?.length || 0,
                ridgeline: lifecycleRidgelineData?.length || 0,
                timeline: lifecycleTimelineData?.length || 0,
                hexbin: lifecycleHexbinData?.length || 0,
                parallel: lifecycleParallelData?.length || 0
            },
            evolutionData: {
                stream: evolutionStreamData?.length || 0,
                bubble: evolutionBubbleData?.length || 0,
                hexbin: evolutionHexbinData?.length || 0,
                parallel: evolutionParallelData?.length || 0,
                tree: evolutionTreeData?.length || 0
            }
        });
        
        // Check if chart initialization function exists
        if (typeof initializeCharts === 'function') {
            console.log('Calling initializeCharts...');
            initializeCharts();
            console.log('Charts initialization completed');
        } else {
            console.error('initializeCharts function not found! Available functions:', Object.keys(window).filter(key => typeof window[key] === 'function'));
        }
        
    } catch (error) {
        console.error('Error during data initialization:', error);
        console.error('Error stack:', error.stack);
    }
} 