/**
 * API Client for CineBook
 * Handles all API requests to the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

class APIClient {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = localStorage.getItem('authToken');
    }

    /**
     * Get authorization headers
     */
    getHeaders(includeAuth = false) {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    /**
     * Handle API response
     */
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({
                detail: 'An error occurred'
            }));
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return null;
    }

    /**
     * Make GET request
     */
    async get(endpoint, params = {}, requiresAuth = false) {
        const url = new URL(`${this.baseURL}${endpoint}`);
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
                url.searchParams.append(key, params[key]);
            }
        });

        const response = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders(requiresAuth),
        });

        return this.handleResponse(response);
    }

    /**
     * Make POST request
     */
    async post(endpoint, data = {}, requiresAuth = false) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: this.getHeaders(requiresAuth),
            body: JSON.stringify(data),
        });

        return this.handleResponse(response);
    }

    /**
     * Make PUT request
     */
    async put(endpoint, data = {}, requiresAuth = false) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'PUT',
            headers: this.getHeaders(requiresAuth),
            body: JSON.stringify(data),
        });

        return this.handleResponse(response);
    }

    /**
     * Make DELETE request
     */
    async delete(endpoint, requiresAuth = false) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'DELETE',
            headers: this.getHeaders(requiresAuth),
        });

        return this.handleResponse(response);
    }

    // ========== GENRE ENDPOINTS ==========

    /**
     * Get all genres
     */
    async getGenres() {
        return this.get('/movies/genres');
    }

    /**
     * Create a new genre (Admin only)
     */
    async createGenre(genreData) {
        return this.post('/movies/genres', genreData, true);
    }

    // ========== MOVIE ENDPOINTS ==========

    /**
     * Get movies with filters
     */
    async getMovies(filters = {}) {
        return this.get('/movies/', filters);
    }

    /**
     * Get single movie by EIDR
     */
    async getMovie(eidr) {
        return this.get(`/movies/${eidr}`);
    }

    /**
     * Create a new movie (Admin only)
     */
    async createMovie(movieData) {
        return this.post('/movies/', movieData, true);
    }

    /**
     * Update movie (Admin only)
     */
    async updateMovie(eidr, movieData) {
        return this.put(`/movies/${eidr}`, movieData, true);
    }

    /**
     * Delete movie (Admin only)
     */
    async deleteMovie(eidr) {
        return this.delete(`/movies/${eidr}`, true);
    }

    // ========== MOVIE DISCOVERY ENDPOINTS ==========

    /**
     * Get now showing movies
     */
    async getNowShowing(limit = 20) {
        return this.get('/movies/discovery/now-showing', { limit });
    }

    /**
     * Get this week's movies
     */
    async getThisWeek(limit = 20) {
        return this.get('/movies/discovery/this-week', { limit });
    }

    /**
     * Get coming soon movies
     */
    async getComingSoon(limit = 20) {
        return this.get('/movies/discovery/coming-soon', { limit });
    }

    // ========== REVIEW ENDPOINTS ==========

    /**
     * Create a review for a movie
     */
    async createReview(eidr, reviewData) {
        return this.post(`/movies/${eidr}/reviews`, {
            ...reviewData,
            movie_eidr: eidr
        }, true);
    }

    /**
     * Get reviews for a movie
     */
    async getMovieReviews(eidr, skip = 0, limit = 10) {
        return this.get(`/movies/${eidr}/reviews`, { skip, limit });
    }

    /**
     * Update a review
     */
    async updateReview(reviewId, reviewData) {
        return this.put(`/movies/reviews/${reviewId}`, reviewData, true);
    }

    /**
     * Delete a review
     */
    async deleteReview(reviewId) {
        return this.delete(`/movies/reviews/${reviewId}`, true);
    }
}

// Create a global API instance
const api = new APIClient();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, api };
}