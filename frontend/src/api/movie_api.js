// teammate file

// src/api/movieApi.js

/**
 * Movie API Client for CineBook (React version)
 *
 * This is basically the same as your teammate's api.js,
 * but wrapped as a class and exported for use in React.
 */

const API_BASE_URL = "http://127.0.0.1:8000/api"; // same as teammate

class MovieAPIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // You can later set a real token after login
  setToken(token) {
    this.token = token;
  }

  getHeaders(auth = false) {
    const h = { "Content-Type": "application/json" };
    if (auth && this.token) {
      h["Authorization"] = `Bearer ${this.token}`;
    }
    return h;
  }

  async request(method, endpoint, data = null, auth = false) {
    const url = new URL(`${this.baseURL}${endpoint}`);
    const opts = { method, headers: this.getHeaders(auth) };

    if (data && method === "GET") {
      Object.keys(data).forEach((k) => {
        if (data[k] !== null && data[k] !== undefined && data[k] !== "") {
          url.searchParams.append(k, data[k]);
        }
      });
    } else if (data) {
      opts.body = JSON.stringify(data);
    }

    const res = await fetch(url, opts);

    if (!res.ok) {
      const err = await res.json().catch(() => ({
        detail: "Error occurred",
      }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    return res.status === 204 ? null : await res.json();
  }

  // ========== GENRES ==========

  async getGenres() {
    return this.request("GET", "/movies/genres");
  }

  async createGenre(data) {
    return this.request("POST", "/movies/genres", data, true);
  }

  // ========== MOVIES ==========

  async getMovies(filters = {}) {
    return this.request("GET", "/movies/", filters);
  }

  async getMovie(eidr) {
    return this.request("GET", `/movies/${eidr}`);
  }

  async createMovie(data) {
    return this.request("POST", "/movies/", data, true);
  }

  async updateMovie(eidr, data) {
    return this.request("PUT", `/movies/${eidr}`, data, true);
  }

  async deleteMovie(eidr) {
    return this.request("DELETE", `/movies/${eidr}`, null, true);
  }

  // ========== DISCOVERY ==========

  async getNowShowing(limit = 20) {
    return this.request("GET", "/movies/discovery/now-showing", { limit });
  }

  async getThisWeek(limit = 20) {
    return this.request("GET", "/movies/discovery/this-week", { limit });
  }

  async getComingSoon(limit = 20) {
    return this.request("GET", "/movies/discovery/coming-soon", { limit });
  }

  // ========== REVIEWS ==========

  async getMovieReviews(eidr, skip = 0, limit = 10) {
    return this.request("GET", `/movies/${eidr}/reviews`, { skip, limit });
  }

  async createReview(eidr, data) {
    return this.request(
      "POST",
      `/movies/${eidr}/reviews`,
      { ...data, movie_eidr: eidr },
      true
    );
  }

  async updateReview(id, data) {
    return this.request("PUT", `/movies/reviews/${id}`, data, true);
  }

  async deleteReview(id) {
    return this.request("DELETE", `/movies/reviews/${id}`, null, true);
  }
}

// We export a *single* shared instance, like your teammate had `const api = new APIClient()`.
export const movieApi = new MovieAPIClient();
