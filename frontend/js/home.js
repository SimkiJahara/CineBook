/**
 * Home Page JavaScript
 * FIXED: Field names to match backend (posterurl, lengthmin, releasedate)
 */
document.addEventListener('DOMContentLoaded', async () => {
    await loadNowShowing();
    await loadThisWeek();
    await loadComingSoon();
});

async function loadNowShowing() {
    const grid = document.getElementById('nowShowingGrid');
    try {
        const movies = await api.getNowShowing(6);
        displayMovies(movies, grid);
    } catch (e) {
        grid.innerHTML = '<div class="error">Failed to load movies</div>';
    }
}

async function loadThisWeek() {
    const grid = document.getElementById('thisWeekGrid');
    try {
        const movies = await api.getThisWeek(6);
        displayMovies(movies, grid);
    } catch (e) {
        grid.innerHTML = '<div class="error">Failed to load movies</div>';
    }
}

async function loadComingSoon() {
    const grid = document.getElementById('comingSoonGrid');
    try {
        const movies = await api.getComingSoon(6);
        displayMovies(movies, grid);
    } catch (e) {
        grid.innerHTML = '<div class="error">Failed to load movies</div>';
    }
}

function displayMovies(movies, container) {
    if (!movies || movies.length === 0) {
        container.innerHTML = '<div class="no-results">No movies available</div>';
        return;
    }
    container.innerHTML = movies.map(m => createMovieCard(m)).join('');
}

function createMovieCard(movie) {
    // FIXED: posterurl instead of poster_url
    const poster = movie.posterurl || 'https://via.placeholder.com/300x450/333/fff?text=No+Poster';
    const rating = movie.average_rating > 0 ? movie.average_rating.toFixed(1) : 'N/A';
    const genres = movie.genres.slice(0, 2).map(g => `<span class="genre-tag">${g.name}</span>`).join('');
    
    return `
        <div class="movie-card" onclick="viewMovie('${movie.eidr}')">
            <img src="${poster}" alt="${movie.title}" class="movie-poster" onerror="this.src='https://via.placeholder.com/300x450/333/fff?text=No+Poster'">
            <div class="movie-info">
                <h3 class="movie-title">${movie.title}</h3>
                <div class="movie-meta">
                    <span class="movie-rating">${rating}</span>
                    <!-- FIXED: lengthmin instead of duration_min -->
                    <span class="movie-duration">${movie.lengthmin || '?'} min</span>
                </div>
                <div class="movie-genres">${genres}</div>
                <p class="movie-language">${movie.language || 'English'}</p>
                <div class="movie-actions">
                    <button class="btn btn-primary" onclick="event.stopPropagation(); bookMovie('${movie.eidr}')">Book Now</button>
                    <button class="btn btn-outline" onclick="event.stopPropagation(); viewMovie('${movie.eidr}')">Details</button>
                </div>
            </div>
        </div>
    `;
}

function searchMovies() {
    const term = document.getElementById('searchInput').value.trim();
    if (term) window.location.href = `movies.html?title=${encodeURIComponent(term)}`;
}

document.getElementById('searchInput')?.addEventListener('keypress', e => {
    if (e.key === 'Enter') searchMovies();
});

function viewMovie(eidr) { window.location.href = `movie-details.html?eidr=${eidr}`; }
function bookMovie(eidr) { window.location.href = `screenings.html?movie=${eidr}`; }