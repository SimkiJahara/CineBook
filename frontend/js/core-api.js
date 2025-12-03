// core-api.js

var API_BASE = "http://127.0.0.1:8000";
var MOVIE_API_BASE = "http://127.0.0.1:8000/api/movies";

function parseJson(res, name) {
  return res.text().then(function (txt) {
    if (!res.ok) {
      throw new Error(name + " failed: " + txt);
    }
    return txt ? JSON.parse(txt) : null;
  });
}

var coreApi = {
  getCities: function () {
    return fetch(API_BASE + "/cities/").then(function (res) {
      return parseJson(res, "getCities");
    });
  },

  getTheatersByCity: function (cityId) {
    return fetch(API_BASE + "/theaters/?city_id=" + cityId).then(function (res) {
      return parseJson(res, "getTheaters");
    });
  },

  getHallsByTheater: function (theaterId) {
    return fetch(API_BASE + "/halls/?theater_id=" + theaterId).then(function (res) {
      return parseJson(res, "getHalls");
    });
  },

  getScreeningsByHallAndDate: function (hallId, date) {
    var params = new URLSearchParams({ hall_id: hallId, show_date: date });
    return fetch(API_BASE + "/screenings/?" + params.toString()).then(function (res) {
      return parseJson(res, "getScreenings");
    });
  },

  getNowShowingMovies: function (limit) {
    if (!limit) limit = 20;
    return fetch(MOVIE_API_BASE + "/discovery/now-showing?limit=" + limit).then(function (res) {
      return parseJson(res, "getNowShowingMovies");
    });
  },

  getMovieByEidr: function (eidr) {
    var encoded = encodeURIComponent(eidr);
    return fetch(MOVIE_API_BASE + "/" + encoded).then(function (res) {
      return parseJson(res, "getMovieByEidr");
    });
  },

  createBooking: function (data) {
    return fetch(API_BASE + "/bookings/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    }).then(function (res) {
      return parseJson(res, "createBooking");
    });
  },

  getMyBookings: function () {
    return fetch(API_BASE + "/bookings/me").then(function (res) {
      return parseJson(res, "getMyBookings");
    }).then(function (result) {
      return Array.isArray(result) ? result : [];
    });
  }
};

console.log("coreApi loaded");
