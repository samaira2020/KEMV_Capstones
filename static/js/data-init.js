// Data initialization script - receives data from Flask template
function initializeData(dataFromServer) {
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
    console.log('Data initialized:', {
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
            marimekko: tacticalMarimekkoData?.length || 0
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
    
    // Initialize charts after data is loaded
    if (typeof initializeCharts === 'function') {
        initializeCharts();
    }
} 