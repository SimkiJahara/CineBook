/**
 * API Client for CineBook
 */
const API_BASE_URL = 'http://localhost:8000/api';

class APIClient {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = localStorage.getItem('authToken');
    }

    getHeaders(auth = false) {
        const h = { 'Content-Type': 'application/json' };
        if (auth && this.token) h['Authorization'] = `Bearer ${this.token}`;
        return h;
    }

    async request(method, endpoint, data = null, auth = false) {
        const url = new URL(`${this.baseURL}${endpoint}`);
        const opts = { method, headers: this.getHeaders(auth) };
        
        if (data && method === 'GET') {
            Object.keys(data).forEach(k => {
                if (data[k] !== null && data[k] !== undefined && data[k] !== '') {
                    url.searchParams.append(k, data[k]);
                }
            });
        } else if (data) {
            opts.body = JSON.stringify(data);
        }
        
        const res = await fetch(url, opts);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Error occurred' }));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }
        return res.status === 204 ? null : await res.json();
    }

    // Genres
    async getGenres() { return this.request('GET', '/movies/genres'); }
    async createGenre(data) { return this.request('POST', '/movies/genres', data, true); }

    // Movies
    async getMovies(filters = {}) { return this.request('GET', '/movies/', filters); }
    async getMovie(eidr) { return this.request('GET', `/movies/${eidr}`); }
    async createMovie(data) { return this.request('POST', '/movies/', data, true); }
    async updateMovie(eidr, data) { return this.request('PUT', `/movies/${eidr}`, data, true); }
    async deleteMovie(eidr) { return this.request('DELETE', `/movies/${eidr}`, null, true); }

    // Discovery
    async getNowShowing(limit = 20) { return this.request('GET', '/movies/discovery/now-showing', { limit }); }
    async getThisWeek(limit = 20) { return this.request('GET', '/movies/discovery/this-week', { limit }); }
    async getComingSoon(limit = 20) { return this.request('GET', '/movies/discovery/coming-soon', { limit }); }

    // Reviews
    async getMovieReviews(eidr, skip = 0, limit = 10) { return this.request('GET', `/movies/${eidr}/reviews`, { skip, limit }); }
    async createReview(eidr, data) { return this.request('POST', `/movies/${eidr}/reviews`, { ...data, movie_eidr: eidr }, true); }
    async updateReview(id, data) { return this.request('PUT', `/movies/reviews/${id}`, data, true); }
    async deleteReview(id) { return this.request('DELETE', `/movies/reviews/${id}`, null, true); }
}

const api = new APIClient();