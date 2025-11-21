/**
 * Movie Details Page JavaScript
 */
let movie = null;
let reviewsSkip = 0;
const reviewsLimit = 5;

document.addEventListener('DOMContentLoaded', async () => {
    const eidr = new URLSearchParams(window.location.search).get('eidr');
    if (!eidr) { showError(); return; }
    await loadMovie(eidr);
    await loadReviews(eidr);
    setupForm();
});

async function loadMovie(eidr) {
    try {
        movie = await api.getMovie(eidr);
        displayMovie();
    } catch (e) { showError(); }
}

function displayMovie() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('movieContent').style.display = 'block';
    document.title = `${movie.title} - CineBook`;
    
    const poster = movie.poster_url || 'https://via.placeholder.com/300x450/333/fff?text=No+Poster';
    document.getElementById('moviePoster').src = poster;
    document.getElementById('movieTitle').textContent = movie.title;
    
    document.getElementById('movieMeta').innerHTML = `
        <span>${movie.rating || 'Not Rated'}</span>
        <span>${movie.duration_min || '?'} min</span>
        <span>${movie.language || 'English'}</span>
        <span>${movie.release_date || 'TBA'}</span>
    `;
    
    document.getElementById('movieGenres').innerHTML = movie.genres.map(g => 
        `<span class="genre-tag">${g.name}</span>`).join('');
    
    document.getElementById('avgRating').textContent = movie.average_rating > 0 ? movie.average_rating.toFixed(1) : '0.0';
    document.getElementById('reviewCount').textContent = `(${movie.review_count} reviews)`;
    document.getElementById('movieDesc').textContent = movie.description || 'No description available.';
    document.getElementById('director').textContent = movie.director || 'Unknown';
    document.getElementById('cast').textContent = movie.cast?.join(', ') || 'Not available';
    
    if (movie.trailer_url) document.getElementById('trailerBtn').style.display = 'inline-block';
}

async function loadReviews(eidr, append = false) {
    try {
        const reviews = await api.getMovieReviews(eidr, reviewsSkip, reviewsLimit);
        displayReviews(reviews, append);
        reviewsSkip += reviews.length;
        document.getElementById('loadMoreBtn').style.display = reviews.length === reviewsLimit ? 'block' : 'none';
    } catch (e) { console.error('Error loading reviews:', e); }
}

function displayReviews(reviews, append = false) {
    const container = document.getElementById('reviewsList');
    if (!append) container.innerHTML = '';
    
    if (reviews.length === 0 && !append) {
        container.innerHTML = '<div class="no-reviews">No reviews yet. Be the first!</div>';
        return;
    }
    
    const html = reviews.map(r => {
        const stars = '★'.repeat(Math.round(r.rating)) + '☆'.repeat(5 - Math.round(r.rating));
        const date = new Date(r.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        return `
            <div class="review-card">
                <div class="review-header">
                    <span class="review-user">User #${r.user_id}</span>
                    <span class="review-stars">${stars}</span>
                </div>
                <div class="review-date">${date}</div>
                ${r.review_text ? `<p class="review-text">${r.review_text}</p>` : ''}
            </div>
        `;
    }).join('');
    
    container.insertAdjacentHTML('beforeend', html);
}

function loadMoreReviews() { loadReviews(movie.eidr, true); }

function setupForm() {
    const isLoggedIn = !!localStorage.getItem('authToken');
    document.getElementById('loginPrompt').style.display = isLoggedIn ? 'none' : 'block';
    document.getElementById('reviewForm').style.display = isLoggedIn ? 'block' : 'none';
    
    document.getElementById('reviewForm').onsubmit = async (e) => {
        e.preventDefault();
        const ratingEl = document.querySelector('input[name="rating"]:checked');
        if (!ratingEl) { alert('Please select a rating'); return; }
        
        try {
            await api.createReview(movie.eidr, {
                rating: parseFloat(ratingEl.value),
                review_text: document.getElementById('reviewText').value.trim() || null
            });
            document.getElementById('reviewForm').style.display = 'none';
            document.getElementById('successMsg').style.display = 'block';
            reviewsSkip = 0;
            await loadReviews(movie.eidr);
            await loadMovie(movie.eidr);
        } catch (e) { alert('Error: ' + e.message); }
    };
}

function showError() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'block';
}

function scrollToReviewForm() {
    if (!localStorage.getItem('authToken')) {
        if (confirm('Login to write a review?')) window.location.href = 'login.html';
        return;
    }
    document.getElementById('reviewFormSection').scrollIntoView({ behavior: 'smooth' });
}

function bookTickets() { window.location.href = `screenings.html?movie=${movie.eidr}`; }
function watchTrailer() { if (movie.trailer_url) window.open(movie.trailer_url, '_blank'); }