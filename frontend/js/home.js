/**
 * Home Page JavaScript
 * Handles loading and displaying movie sections
 */

// Load movies on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadNowShowing();
    await loadThisWeek();
    await loadComingSoon();
});

/**
 * Load Now Showing movies
 */
async function loadNowShowing() {
    const grid = document.getElementById('nowShowingGrid');
    
    try {
        const movies = await api.getNowShowing(6);
        displayMovies(movies, grid);
    } catch (error) {
        console.error('Error loading now showing movies:', error);
        grid.innerHTML = '<div class="error">Failed to load movies. Please try again later.</div>';
    }
}

/**
 * Load This Week movies
 */
async function loadThisWeek() {
    const grid = document.getElementById('thisWeekGrid');
    
    try {
        const movies = await api.getThisWeek(6);
        displayMovies(movies, grid);
    } catch (error) {
        console.error('Error loading this week movies:', error);
        grid.innerHTML = '<div class="error">Failed to load movies. Please try again later.</div>';
    }
}

/**
 * Load Coming Soon movies
 */
async function loadComingSoon() {
    const grid = document.getElementById('comingSoonGrid');
    
    try {
        const movies = await api.getComingSoon(6);
        displayMovies(movies, grid);
    } catch (error) {
        console.error('Error loading coming soon movies:', error);
        grid.innerHTML = '<div class="error">Failed to load movies. Please try again later.</div>';
    }
}

/**
 * Display movies in grid
 */
function displayMovies(movies, container) {
    if (!movies || movies.length === 0) {
        container.innerHTML = '<div class="no-results">No movies available at this time.</div>';
        return;
    }

    container.innerHTML = movies.map(movie => createMovieCard(movie)).join('');
}

/**
 * Create movie card HTML
 */
function createMovieCard(movie) {
    const posterUrl = movie.poster_url || 'images/placeholder-poster.jpg';
    const rating = movie.average_rating > 0 ? movie.average_rating.toFixed(1) : 'N/A';
    const genres = movie.genres.slice(0, 3).map(g => g.name).join(', ');
    
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
 * Search movies from hero section
 */
function searchMovies() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    if (searchTerm) {
        window.location.href = `movies.html?title=${encodeURIComponent(searchTerm)}`;
    }
}

// Allow Enter key in search
document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchMovies();
    }
});

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
    // Redirect to screenings page with movie filter
    window.location.href = `screenings.html?movie=${eidr}`;
}

// Style for error message
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
`;
document.head.appendChild(style);