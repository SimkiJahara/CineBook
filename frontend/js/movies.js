/**
 * Movies Catalogue Page JavaScript
 */
let currentPage = 1;
const perPage = 20;
let totalMovies = 0;

document.addEventListener('DOMContentLoaded', async () => {
    await loadGenres();
    loadURLParams();
    await loadMovies();
});

async function loadGenres() {
    try {
        const genres = await api.getGenres();
        const container = document.getElementById('genreFilter');
        container.innerHTML = genres.map(g => `
            <div class="checkbox-item">
                <input type="checkbox" id="g-${g.id}" value="${g.name}" onchange="applyFilters()">
                <label for="g-${g.id}">${g.name}</label>
            </div>
        `).join('');
    } catch (e) { console.error('Error loading genres:', e); }
}

function loadURLParams() {
    const params = new URLSearchParams(window.location.search);
    const title = params.get('title');
    if (title) document.getElementById('titleFilter').value = title;
}

async function loadMovies() {
    const grid = document.getElementById('moviesGrid');
    grid.innerHTML = '<div class="loading">Loading movies...</div>';
    
    try {
        const filters = getFilters();
        const movies = await api.getMovies(filters);
        totalMovies = movies.length;
        displayMovies(movies, grid);
        updateResultsCount();
        updatePagination();
    } catch (e) {
        grid.innerHTML = '<div class="error">Failed to load movies</div>';
    }
}

function getFilters() {
    const f = { skip: (currentPage - 1) * perPage, limit: perPage };
    
    const title = document.getElementById('titleFilter').value.trim();
    if (title) f.title = title;
    
    const genres = Array.from(document.querySelectorAll('#genreFilter input:checked')).map(c => c.value);
    if (genres.length) f.genres = genres.join(',');
    
    const lang = document.getElementById('languageFilter').value;
    if (lang) f.languages = lang;
    
    const minD = document.getElementById('minDuration').value;
    if (minD) f.min_duration = parseInt(minD);
    
    const maxD = document.getElementById('maxDuration').value;
    if (maxD) f.max_duration = parseInt(maxD);
    
    const rating = document.getElementById('ratingFilter').value;
    if (rating) f.age_rating = rating;
    
    f.sort_by = document.getElementById('sortBy').value;
    f.order = document.getElementById('sortOrder').value;
    
    return f;
}

function displayMovies(movies, container) {
    if (!movies || movies.length === 0) {
        container.innerHTML = '<div class="no-results">No movies found</div>';
        return;
    }
    container.innerHTML = movies.map(m => createCard(m)).join('');
}

function createCard(m) {
    const poster = m.poster_url || 'https://via.placeholder.com/300x450/333/fff?text=No+Poster';
    const rating = m.average_rating > 0 ? m.average_rating.toFixed(1) : 'N/A';
    const genres = m.genres.slice(0, 2).map(g => `<span class="genre-tag">${g.name}</span>`).join('');
    
    return `
        <div class="movie-card" onclick="viewMovie('${m.eidr}')">
            <img src="${poster}" alt="${m.title}" class="movie-poster" onerror="this.src='https://via.placeholder.com/300x450/333/fff?text=No+Poster'">
            <div class="movie-info">
                <h3 class="movie-title">${m.title}</h3>
                <div class="movie-meta">
                    <span class="movie-rating">${rating}</span>
                    <span class="movie-duration">${m.duration_min || '?'} min</span>
                </div>
                <div class="movie-genres">${genres}</div>
                <p class="movie-language">${m.language || 'English'}</p>
                <div class="movie-actions">
                    <button class="btn btn-primary" onclick="event.stopPropagation(); bookMovie('${m.eidr}')">Book</button>
                    <button class="btn btn-outline" onclick="event.stopPropagation(); viewMovie('${m.eidr}')">Details</button>
                </div>
            </div>
        </div>
    `;
}

function updateResultsCount() {
    document.getElementById('resultsCount').textContent = `${totalMovies} movies found`;
}

function updatePagination() {
    const pages = Math.ceil(totalMovies / perPage);
    const container = document.getElementById('pagination');
    if (pages <= 1) { container.innerHTML = ''; return; }
    
    let html = `<button ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">Prev</button>`;
    for (let i = 1; i <= pages; i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
    }
    html += `<button ${currentPage === pages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">Next</button>`;
    container.innerHTML = html;
}

function goToPage(p) { currentPage = p; loadMovies(); window.scrollTo({ top: 0, behavior: 'smooth' }); }
function applyFilters() { currentPage = 1; loadMovies(); }
function clearFilters() {
    document.getElementById('titleFilter').value = '';
    document.getElementById('languageFilter').value = '';
    document.getElementById('minDuration').value = '';
    document.getElementById('maxDuration').value = '';
    document.getElementById('ratingFilter').value = '';
    document.getElementById('sortBy').value = 'title';
    document.getElementById('sortOrder').value = 'asc';
    document.querySelectorAll('#genreFilter input').forEach(c => c.checked = false);
    currentPage = 1;
    loadMovies();
}

function viewMovie(eidr) { window.location.href = `movie-details.html?eidr=${eidr}`; }
function bookMovie(eidr) { window.location.href = `screenings.html?movie=${eidr}`; }