// js/bookings.js

function getEventDate(booking) {
  var screening = booking.screening || {};
  var dateStr = screening.show_date || booking.created_at;
  var timeStr = screening.start_time || "00:00";

  if (!dateStr) {
    return null;
  }

  try {
    return new Date(dateStr + "T" + timeStr);
  } catch (e) {
    return null;
  }
}

function createRow(booking) {
  var tr = document.createElement("tr");
  var screening = booking.screening || {};

  var movieTitle = "Movie #" + (booking.screening_id || booking.id);
  if (screening.movie && screening.movie.title) {
    movieTitle = screening.movie.title;
  } else if (booking.movie_title) {
    movieTitle = booking.movie_title;
  }

  var dateText = "-";
  if (screening.show_date) {
    dateText = screening.show_date;
  } else if (booking.show_date) {
    dateText = booking.show_date;
  } else if (booking.created_at) {
    dateText = booking.created_at.slice(0, 10);
  }

  var timeText = screening.start_time || booking.start_time || "--";

  var hallName = "N/A";
  if (screening.hall && screening.hall.name) {
    hallName = screening.hall.name;
  } else if (booking.hall_name) {
    hallName = booking.hall_name;
  } else if (screening.hall_id) {
    hallName = "Hall " + screening.hall_id;
  }

  var theaterName = "—";
  if (screening.hall && screening.hall.theater && screening.hall.theater.name) {
    theaterName = screening.hall.theater.name;
  } else if (booking.theater_name) {
    theaterName = booking.theater_name;
  }

  var seatsText = "—";
  if (booking.seats && booking.seats.length > 0) {
    seatsText = booking.seats
      .map(function (seat) {
        return seat.seat_label || seat.code || "Seat";
      })
      .join(", ");
  }

  var status = (booking.payment_status || "PAID").toUpperCase();
  var statusClass = status === "PAID" ? "status-paid" : "status-unpaid";

  tr.innerHTML =
    "<td>" +
    movieTitle +
    "</td>" +
    "<td>" +
    dateText +
    "</td>" +
    "<td>" +
    timeText +
    "</td>" +
    "<td>" +
    seatsText +
    "</td>" +
    "<td>" +
    theaterName +
    "</td>" +
    "<td>" +
    hallName +
    "</td>" +
    '<td><span class="status-pill ' +
    statusClass +
    '">' +
    status +
    "</span></td>";

  return tr;
}

function setStatus(msg) {
  var el = document.getElementById("statusMsg");
  if (!el) {
    return;
  }
  el.textContent = msg || "";
}

document.addEventListener("DOMContentLoaded", function () {
  var upcomingBody = document.getElementById("upcomingBody");
  var pastBody = document.getElementById("pastBody");
  var upcomingEmpty = document.getElementById("upcomingEmpty");
  var pastEmpty = document.getElementById("pastEmpty");

  setStatus("Loading your bookings...");

  coreApi
    .getMyBookings()
    .then(function (bookings) {
      if (!Array.isArray(bookings) || bookings.length === 0) {
        setStatus("");
        upcomingEmpty.classList.remove("hidden");
        pastEmpty.classList.remove("hidden");
        return;
      }

      var now = new Date();
      var upcoming = [];
      var past = [];

      bookings.forEach(function (b) {
        var d = getEventDate(b);
        if (d && d >= now) {
          upcoming.push(b);
        } else {
          past.push(b);
        }
      });

      upcoming.sort(function (a, b) {
        var da = getEventDate(a) || now;
        var db = getEventDate(b) || now;
        return da - db;
      });

      past.sort(function (a, b) {
        var da = getEventDate(a) || now;
        var db = getEventDate(b) || now;
        return db - da;
      });

      if (upcoming.length === 0) {
        upcomingEmpty.classList.remove("hidden");
      } else {
        upcoming.forEach(function (b) {
          upcomingBody.appendChild(createRow(b));
        });
      }

      if (past.length === 0) {
        pastEmpty.classList.remove("hidden");
      } else {
        past.forEach(function (b) {
          pastBody.appendChild(createRow(b));
        });
      }

      setStatus("");
    })
    .catch(function () {
      setStatus("Could not load bookings. Please try again.");
    });
});
