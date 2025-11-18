/**
 * Movies Page JavaScript
 * Handles filtering, sorting, and pagination
 */

let currentPage = 1;
const moviesPerPage = 20;
let totalMovies = 0;
let allGenres = [];

// Load initial data
document.addEventListener('DOMContentLoaded', async () => {
    await loadGenres();
    await loadURLParams();
    await loadMovies();
});

/**
 * Load genres for filter
 */
async function loadGenres() {
    try {
        allGenres = await api.getGenres();
        const genreFilter = document.getElementById('genreFilter');
        
        genreFilter.innerHTML = allGenres.map(genre => `
            <div class="checkbox-item">
                <input type="checkbox" id="genre-${genre.id}" value="${genre.name}" 
                       onchange="applyFilters()">
                <label for="genre-${genre.id}">${genre.name}</label>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading genres:', error);
    }
}

/**
 * Load parameters from URL
 */
function loadURLParams() {
    const params = new URLSearchParams(window.location.search);
    
    // Set title filter
    const title = params.get('title');
    if (title) {
        document.getElementById('titleFilter').value = title;
    }
    
    // Set filter based on discovery category
    const filter = params.get('filter');
    if (filter) {
        // Handle specific discovery filters
        // These will be applied in loadMovies
    }
}

/**
 * Load movies with current filters
 */
async function loadMovies() {
    const grid = document.getElementById('moviesGrid');
    grid.innerHTML = '<div class="loading">Loading movies...</div>';
    
    try {
        const filters = getFilterParams();
        const movies = await api.getMovies(filters);
        
        totalMovies = movies.length; // In a real app, you'd get this from the API response
        displayMovies(movies);
        updateResultsCount(movies.length);
        updatePagination();
    } catch (error) {
        console.error('Error loading movies:', error);
        grid.innerHTML = '<div class="error">Failed to load movies. Please try again later.</div>';
    }
}

/**
 * Get filter parameters from form
 */
function getFilterParams() {
    const params = {
        skip: (currentPage - 1) * moviesPerPage,
        limit: moviesPerPage
    };
    
    // Title filter
    const title = document.getElementById('titleFilter').value.trim();
    if (title) {
        params.title = title;
    }
    
    // Genre filter
    const selectedGenres = Array.from(document.querySelectorAll('#genreFilter input:checked'))
        .map(cb => cb.value);
    if (selectedGenres.length > 0) {
        params.genres = selectedGenres.join(',');
    }
    
    // Language filter
    const language = document.getElementById('languageFilter').value;
    if (language) {
        params.languages = language;
    }
    
    // Duration filter
    const minDuration = document.getElementById('minDuration').value;
    if (minDuration) {
        params.min_duration = parseInt(minDuration);
    }
    
    const maxDuration = document.getElementById('maxDuration').value;
    if (maxDuration) {
        params.max_duration = parseInt(maxDuration);
    }
    
    // Age rating filter
    const rating = document.getElementById('ratingFilter').value;
    if (rating) {
        params.age_rating = rating;
    }
    
    // Sort parameters
    params.sort_by = document.getElementById('sortBy').value;
    params.order = document.getElementById('sortOrder').value;
    
    // Check for discovery filter from URL
    const urlParams = new URLSearchParams(window.location.search);
    const discoveryFilter = urlParams.get('filter');
    if (discoveryFilter) {
        // Handle special discovery endpoints
        return { limit: moviesPerPage };
    }
    
    return params;
}

/**
 * Display movies in grid
 */
function displayMovies(movies) {
    const grid = document.getElementById('moviesGrid');
    
    if (!movies || movies.length === 0) {
        grid.innerHTML = '<div class="no-results">No movies found matching your criteria.</div>';
        return;
    }
    
    grid.innerHTML = movies.map(movie => createMovieCard(movie)).join('');
}

/**
 * Create movie card HTML
 */
function createMovieCard(movie) {
    const posterUrl = movie.poster_url || 'images/placeholder-poster.jpg';
    const rating = movie.average_rating > 0 ? movie.average_rating.toFixed(1) : 'N/A';
    const reviewText = movie.review_count === 1 ? 'review' : 'reviews';
    
    return `
        <div class="movie-card" onclick="viewMovieDetails('${movie.eidr}')">
            <img src="${posterUrl}" alt="${movie.title}" class="movie-poster"
                 onerror="this.src='images/placeholder-poster.jpg'">
            <div class="movie-info">
                <h3 class="movie-title">${movie.title}</h3>
                <div class="movie-meta">
                    <span class="movie-rating">${rating}</span>
                    <span class="movie-duration">${movie.duration_min} min</span>
                </div>
                <div class="movie-genres">
                    ${movie.genres.slice(0, 3).map(genre => 
                        `<span class="genre-tag">${genre.name}</span>`
                    ).join('')}
                </div>
                <p class="movie-language">Language: ${movie.language}</p>
                <p class="movie-reviews">${movie.review_count} ${reviewText}</p>
                <div class="movie-actions">
                    <button class="btn btn-primary" onclick="event.stopPropagation(); bookNow('${movie.eidr}')">
                        Book Now
                    </button>
                    <button class="btn btn-outline" onclick="event.stopPropagation(); viewMovieDetails('${movie.eidr}')">
                        Details
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Update results count
 */
function updateResultsCount(count) {
    const resultsCount = document.getElementById('resultsCount');
    const start = (currentPage - 1) * moviesPerPage + 1;
    const end = Math.min(currentPage * moviesPerPage, count);
    resultsCount.textContent = `Showing ${start}-${end} of ${count} movies`;
}

/**
 * Update pagination controls
 */
function updatePagination() {
    const pagination = document.getElementById('pagination');
    const totalPages = Math.ceil(totalMovies / moviesPerPage);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = `
        <button ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">
            Previous
        </button>
    `;
    
    // Show page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `
                <button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">
                    ${i}
                </button>
            `;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += '<span class="pagination-ellipsis">...</span>';
        }
    }
    
    html += `
        <button ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">
            Next
        </button>
    `;
    
    pagination.innerHTML = html;
}

/**
 * Go to specific page
 */
function goToPage(page) {
    currentPage = page;
    loadMovies();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Apply filters
 */
function applyFilters() {
    currentPage = 1; // Reset to first page
    loadMovies();
}

/**
 * Clear all filters
 */
function clearFilters() {
    document.getElementById('titleFilter').value = '';
    document.getElementById('languageFilter').value = '';
    document.getElementById('minDuration').value = '';
    document.getElementById('maxDuration').value = '';
    document.getElementById('ratingFilter').value = '';
    document.getElementById('sortBy').value = 'title';
    document.getElementById('sortOrder').value = 'asc';
    
    // Clear genre checkboxes
    document.querySelectorAll('#genreFilter input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
    
    currentPage = 1;
    loadMovies();
}

/**
 * View movie details
 */
function viewMovieDetails(eidr) {
    window.location.href = `movie-details.html?eidr=${eidr}`;
}

/**
 * Book movie
 */
function bookNow(eidr) {
    window.location.href = `screenings.html?movie=${eidr}`;
}

// Add styles for additional elements
const style = document.createElement('style');
style.textContent = `
    .error {
        text-align: center;
        padding: 60px 20px;
        color: var(--primary-color);
        font-size: 16px;
    }
    
    .no-results {
        text-align: center;
        padding: 60px 20px;
        color: var(--text-secondary);
        font-size: 16px;
    }
    
    .movie-reviews {
        color: var(--text-secondary);
        font-size: 13px;
        margin-bottom: 12px;
    }
    
    .pagination-ellipsis {
        padding: 10px;
        color: var(--text-secondary);
    }
`;
document.head.appendChild(style);