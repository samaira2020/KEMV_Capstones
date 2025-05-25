document.addEventListener('DOMContentLoaded', function() {
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    const genreFilter = document.getElementById('genre-filter');
    const platformFilter = document.getElementById('platform-filter');
    const yearStartInput = document.getElementById('year-start');
    const yearEndInput = document.getElementById('year-end');
    const filterForm = document.getElementById('filter-form');
    const yearRangeDisplay = document.getElementById('year-range-display');

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

    // Update year range display as sliders are moved
    if (yearStartInput && yearEndInput && yearRangeDisplay) {
        yearStartInput.addEventListener('input', updateYearRangeDisplay);
        yearEndInput.addEventListener('input', updateYearRangeDisplay);
    }

    function updateYearRangeDisplay() {
        yearRangeDisplay.textContent = `${yearStartInput.value} - ${yearEndInput.value}`;
    }

    // --- Chart Rendering Functions using Chart.js ---

    // Function to render Games Per Year Chart
    function renderGamesPerYearChart(data) {
        const ctx = document.getElementById('gamesPerYearChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item._id).sort(), // Assuming _id is the year
                datasets: [{
                    label: 'Number of Games',
                    data: data.map(item => item.count),
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Year'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Number of Games'
                        },
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Games Released Per Year'
                    }
                }
            }
        });
    }

    // Function to render Game Share by Publisher Chart (Pie Chart)
    function renderPublisherShareChart(data) {
        // Take top 10 publishers
        const top10Data = data.slice(0, 10);

        const ctx = document.getElementById('publisherShareChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: top10Data.map(item => item._id),
                datasets: [{
                    label: 'Game Count',
                    data: top10Data.map(item => item.count),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966CC', '#FF9F40',
                        '#FFCD56', '#4CC0C0', '#9666CC', '#FF9940'
                    ],
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Game Share by Publisher (Top 10)'
                    }
                }
            }
        });
    }

     // Function to render Game Distribution by Platform Chart (Bar Chart)
     function renderPlatformChart(data) {
        // Sort by count descending and take top N if needed, or use all data
         const sortedData = data.sort((a, b) => b.count - a.count);

         const ctx = document.getElementById('platformChart').getContext('2d');
         new Chart(ctx, {
             type: 'bar',
             data: {
                 labels: sortedData.map(item => item._id),
                 datasets: [{
                     label: 'Number of Games',
                     data: sortedData.map(item => item.count),
                     backgroundColor: 'rgba(54, 162, 235, 0.6)',
                     borderColor: 'rgba(54, 162, 235, 1)',
                     borderWidth: 1
                 }]
             },
             options: {
                 responsive: true,
                 scales: {
                     y: {
                         beginAtZero: true,
                         title: {
                             display: true,
                             text: 'Number of Games'
                         }
                     },
                     x: {
                         title: {
                             display: true,
                             text: 'Platform'
                         }
                     }
                 },
                 plugins: {
                     title: {
                         display: true,
                         text: 'Game Distribution by Platform'
                     },
                      legend: {
                         display: false // Hide legend for single dataset bar chart
                     }
                 }
             }
         });
     }

     // Function to render Game Distribution by Genre Chart (Bar Chart)
     function renderGenreChart(data) {
         // Sort by count descending and take top N if needed, or use all data
         const sortedData = data.sort((a, b) => b.count - a.count);

         const ctx = document.getElementById('genreChart').getContext('2d');
         new Chart(ctx, {
             type: 'bar',
             data: {
                 labels: sortedData.map(item => item._id),
                 datasets: [{
                     label: 'Number of Games',
                     data: sortedData.map(item => item.count),
                     backgroundColor: 'rgba(255, 99, 132, 0.6)',
                     borderColor: 'rgba(255, 99, 132, 1)',
                     borderWidth: 1
                 }]
             },
             options: {
                 responsive: true,
                 scales: {
                     y: {
                         beginAtZero: true,
                         title: {
                             display: true,
                             text: 'Number of Games'
                         }
                     },
                     x: {
                         title: {
                             display: true,
                             text: 'Genre'
                         }
                     }
                 },
                 plugins: {
                     title: {
                         display: true,
                         text: 'Game Distribution by Genre'
                     },
                     legend: {
                         display: false // Hide legend for single dataset bar chart
                     }
                 }
             }
         });
     }

     // Function to render Average Rating by Platform Chart (Bar Chart)
     function renderAvgRatingPlatformChart(data) {
         // Sort by average rating descending and take top 10
         const top10Data = data.sort((a, b) => b.average_rating - a.average_rating).slice(0, 10);

         const ctx = document.getElementById('avgRatingPlatformChart').getContext('2d');
         new Chart(ctx, {
             type: 'bar',
             data: {
                 labels: top10Data.map(item => item._id),
                 datasets: [{
                     label: 'Average Rating',
                     data: top10Data.map(item => item.average_rating),
                     backgroundColor: 'rgba(153, 102, 255, 0.6)',
                     borderColor: 'rgba(153, 102, 255, 1)',
                     borderWidth: 1
                 }]
             },
             options: {
                 responsive: true,
                 scales: {
                     y: {
                         beginAtZero: true,
                         title: {
                             display: true,
                             text: 'Average Rating'
                         }
                     },
                     x: {
                         title: {
                             display: true,
                             text: 'Platform'
                         }
                     }
                 },
                 plugins: {
                     title: {
                         display: true,
                         text: 'Average Rating by Platform (Top 10)'
                     },
                     legend: {
                         display: false // Hide legend
                     }
                 }
             }
         });
     }

     // Function to render Average Rating by Developer Chart (Bar Chart)
     function renderAvgRatingDeveloperChart(data) {
         // Sort by average rating descending and take top 10
         const top10Data = data.sort((a, b) => b.average_rating - a.average_rating).slice(0, 10);

         const ctx = document.getElementById('avgRatingDeveloperChart').getContext('2d');
         new Chart(ctx, {
             type: 'bar',
             data: {
                 labels: top10Data.map(item => item._id),
                 datasets: [{
                     label: 'Average Rating',
                     data: top10Data.map(item => item.average_rating),
                     backgroundColor: 'rgba(255, 159, 64, 0.6)',
                     borderColor: 'rgba(255, 159, 64, 1)',
                     borderWidth: 1
                 }]
             },
             options: {
                 responsive: true,
                 scales: {
                     y: {
                         beginAtZero: true,
                         title: {
                             display: true,
                             text: 'Average Rating'
                         }
                     },
                     x: {
                         title: {
                             display: true,
                             text: 'Developer'
                         }
                     }
                 },
                 plugins: {
                     title: {
                         display: true,
                         text: 'Average Rating by Developer (Top 10)'
                     },
                      legend: {
                         display: false // Hide legend
                     }
                 }
             }
         });
     }

    // Function to render all charts using the global data variables
    function renderAllCharts() {
        // Clear existing charts if they exist
        // (This is a simple approach; a more robust method would involve destroying Chart.js instances)
        // However, since we are replacing the main-content div on filter apply, old charts are removed.

        // Check if global data variables exist and are not empty before rendering
        if (typeof gamesPerYear !== 'undefined' && gamesPerYear.length > 0) {
             renderGamesPerYearChart(gamesPerYear);
         } else {
             console.warn("No data for Games Per Year chart.");
             // Optionally display a message on the canvas
             const ctx = document.getElementById('gamesPerYearChart').getContext('2d');
             ctx.font = '18px Arial';
             ctx.fillStyle = 'white';
             ctx.textAlign = 'center';
             ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
         }

         if (typeof publisherCounts !== 'undefined' && publisherCounts.length > 0) {
             renderPublisherShareChart(publisherCounts);
         } else {
             console.warn("No data for Publisher Share chart.");
             const ctx = document.getElementById('publisherShareChart').getContext('2d');
             ctx.font = '18px Arial';
             ctx.fillStyle = 'white';
             ctx.textAlign = 'center';
             ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
         }

         if (typeof platformCounts !== 'undefined' && platformCounts.length > 0) {
             renderPlatformChart(platformCounts);
         } else {
             console.warn("No data for Platform Distribution chart.");
             const ctx = document.getElementById('platformChart').getContext('2d');
             ctx.font = '18px Arial';
             ctx.fillStyle = 'white';
             ctx.textAlign = 'center';
             ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
         }

         if (typeof genreCounts !== 'undefined' && genreCounts.length > 0) {
             renderGenreChart(genreCounts);
         } else {
              console.warn("No data for Genre Distribution chart.");
              const ctx = document.getElementById('genreChart').getContext('2d');
              ctx.font = '18px Arial';
              ctx.fillStyle = 'white';
              ctx.textAlign = 'center';
              ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
         }

         if (typeof avgRatingPlatform !== 'undefined' && avgRatingPlatform.length > 0) {
              renderAvgRatingPlatformChart(avgRatingPlatform);
          } else {
              console.warn("No data for Average Rating by Platform chart.");
              const ctx = document.getElementById('avgRatingPlatformChart').getContext('2d');
              ctx.font = '18px Arial';
              ctx.fillStyle = 'white';
              ctx.textAlign = 'center';
              ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
          }

          if (typeof avgRatingDeveloper !== 'undefined' && avgRatingDeveloper.length > 0) {
              renderAvgRatingDeveloperChart(avgRatingDeveloper);
          } else {
              console.warn("No data for Average Rating by Developer chart.");
              const ctx = document.getElementById('avgRatingDeveloperChart').getContext('2d');
              ctx.font = '18px Arial';
              ctx.fillStyle = 'white';
              ctx.textAlign = 'center';
              ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
          }

    }

    // Initial rendering when the page loads
    renderAllCharts();

    // Event listener for the form submission
    if (filterForm) {
        filterForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission
            const formData = new FormData(filterForm);
            const queryParams = new URLSearchParams(formData).toString();
            window.location.href = '/' + (queryParams ? '?' + queryParams : ''); // Redirect with query params
        });
    }

    // Initial update of year range display on page load
    if (yearStartInput && yearEndInput && yearRangeDisplay) {
        updateYearRangeDisplay();
    }

}); 