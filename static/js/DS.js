document.addEventListener('DOMContentLoaded', function() {
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    const genreFilter = document.getElementById('genre-filter');
    const platformFilter = document.getElementById('platform-filter');
    const yearStartInput = document.getElementById('year-start');
    const yearEndInput = document.getElementById('year-end');

    // Function to fetch data from Flask back-end
    function fetchDataAndRender(filters = {}) {
        // Construct query string from filters
        const params = new URLSearchParams();
        if (filters.genres) {
            filters.genres.forEach(genre => params.append('genre', genre));
        }
        if (filters.platforms) {
            filters.platforms.forEach(platform => params.append('platform', platform));
        }
        if (filters.year_start) {
            params.append('year_start', filters.year_start);
        }
        if (filters.year_end) {
            params.append('year_end', filters.year_end);
        }

        const url = '/' + (params.toString() ? '?' + params.toString() : '');

        fetch(url)
            .then(response => response.text()) // Fetch HTML content for now
            .then(html => {
                // Since Flask renders the whole page, we replace the content
                // A more advanced approach would be to create a dedicated API endpoint
                // that returns JSON data, and update parts of the page dynamically.
                // For simplicity, we'll replace the main content area.
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newMainContent = doc.querySelector('.main-content');
                const mainContent = document.querySelector('.main-content');
                if (newMainContent && mainContent) {
                    mainContent.innerHTML = newMainContent.innerHTML;
                    // Re-run the renderCharts function after updating content
                    renderCharts();
                }

                 // Update filter selections to reflect applied filters (optional, depends on desired UX)
                 // This would require the backend to return the applied filters or the full state.
                 // For now, the page reload effectively resets the selection visually.
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    // Function to render Plotly charts
    function renderCharts() {
        // Get data from the HTML (passed via Jinja and embedded as JSON strings)
        // We need to find a way to pass this data from Flask to JS.
        // A common way is to embed JSON data in a script tag in index.html.

        // Example: Assuming you have script tags like this in index.html:
        // <script id="games-per-year-data" type="application/json">{{ games_per_year_data | safe }}</script>
        // And chart containers with IDs like 'games-per-year-chart'

        const chartDataElements = {
            'games-per-year-chart': 'games-per-year-data',
            'game-share-publisher-chart': 'game-share-pub-data',
            'top-publishers-chart': 'top-publishers-data',
            'avg-rating-platform-chart': 'avg-rating-platform-data',
            'avg-rating-developer-chart': 'avg-rating-dev-data'
        };

        for (const [chartId, dataId] of Object.entries(chartDataElements)) {
            const dataElement = document.getElementById(dataId);
            const chartContainer = document.getElementById(chartId);

            if (dataElement && chartContainer) {
                try {
                    const data = JSON.parse(dataElement.textContent);
                    let layout = {}; // Default layout
                    let plotData = []; // Plotly data array

                    // Define plot data and layout based on chart type
                    if (chartId === 'games-per-year-chart') {
                        // Line chart
                        plotData = [{
                            x: data.map(item => item.Year),
                            y: data.map(item => item.Count),
                            mode: 'lines+markers',
                            type: 'scatter'
                        }];
                        layout = { title: 'Games Released Per Year' };
                    } else if (chartId === 'game-share-publisher-chart') {
                         // Pie chart
                         plotData = [{
                            labels: data.map(item => item.Publisher),
                            values: data.map(item.Count),
                            type: 'pie'
                         }];
                         layout = { title: 'Game Share Distribution by Top Publishers' };
                    } else if (chartId === 'top-publishers-chart') {
                        // Bar chart
                         plotData = [{
                            x: data.map(item => item.Publisher),
                            y: data.map(item.Count),
                            type: 'bar'
                         }];
                         layout = { title: 'Top Publishers by Game Count' };
                    } else if (chartId === 'avg-rating-platform-chart') {
                         // Bar chart
                         plotData = [{
                            x: data.map(item => item.Platform),
                            y: data.map(item['Average Rating']),
                            type: 'bar'
                         }];
                         layout = { title: 'Average Rating by Platform' };
                    } else if (chartId === 'avg-rating-developer-chart') {
                         // Bar chart
                         plotData = [{
                            x: data.map(item => item.Developer),
                            y: data.map(item['Average Rating']),
                            type: 'bar'
                         }];
                         layout = { title: 'Average Rating Per Developer' };
                    }

                    Plotly.newPlot(chartContainer, plotData, layout);

                } catch (e) {
                    console.error(`Error parsing or rendering chart data for ${chartId}:`, e);
                     chartContainer.innerHTML = '<p>Error loading chart.</p>'; // Indicate error on the page
                }
            } else {
                // console.warn(`Chart container ${chartId} or data element ${dataId} not found.`);
            }
        }
    }

    // Event listener for the Apply Filters button
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            const selectedGenres = Array.from(genreFilter.selectedOptions).map(option => option.value);
            const selectedPlatforms = Array.from(platformFilter.selectedOptions).map(option => option.value);
            const yearStart = yearStartInput.value;
            const yearEnd = yearEndInput.value;

            const filters = {
                genres: selectedGenres,
                platforms: selectedPlatforms,
                year_start: yearStart,
                year_end: yearEnd
            };

            fetchDataAndRender(filters);
        });
    }

    // Initial rendering when the page loads
     renderCharts(); // Render charts with initial data from Flask

    // Note: Initial data for the table, KPIs, and Highly Rated Games list
    // is rendered directly by Jinja in index.html on the initial page load.
    // The fetchDataAndRender function currently replaces the entire main content,
    // which re-renders these sections as well.
}); 