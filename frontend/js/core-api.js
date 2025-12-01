const API_BASE = "http://127.0.0.1:8000";
const MOVIE_API_BASE = "http://127.0.0.1:8000/api/movies";

async function jsonOrThrow(res, label) {
  const text = await res.text();
  if (!res.ok) throw new Error(`${label} failed: ${text}`);
  return text ? JSON.parse(text) : null;
}

const coreApi = {
  async getCities() {
    const r = await fetch(`${API_BASE}/cities/`);
    return jsonOrThrow(r, "getCities");
  },

  async getTheatersByCity(cityId) {
    const r = await fetch(`${API_BASE}/theaters/?city_id=${cityId}`);
    return jsonOrThrow(r, "getTheaters");
  },

  async getHallsByTheater(tid) {
    const r = await fetch(`${API_BASE}/halls/?theater_id=${tid}`);
    return jsonOrThrow(r, "getHalls");
  },

  async getScreeningsByHallAndDate(hallId, date) {
    const params = new URLSearchParams({ hall_id: hallId, show_date: date });
    const r = await fetch(`${API_BASE}/screenings/?${params.toString()}`);
    return jsonOrThrow(r, "getScreenings");
  },

  async getNowShowingMovies(limit = 20) {
    const r = await fetch(
      `${MOVIE_API_BASE}/discovery/now-showing?limit=${limit}`
    );
    return jsonOrThrow(r, "getNowShowingMovies");
  },

  async getMovieByEidr(eidr) {
    const encoded = encodeURIComponent(eidr);
    const r = await fetch(`${MOVIE_API_BASE}/${encoded}`);
    return jsonOrThrow(r, "getMovieByEidr");
  },

  async createBooking(data) {
    const r = await fetch(`${API_BASE}/bookings/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return jsonOrThrow(r, "createBooking");
  },

  async getMyBookings() {
    const r = await fetch(`${API_BASE}/bookings/me`);
    const result = await jsonOrThrow(r, "getMyBookings");
    return Array.isArray(result) ? result : [];
  },
};

console.log("coreApi loaded:", coreApi);
