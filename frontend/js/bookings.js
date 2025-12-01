// js/bookings.js

// small helper: parse date+time safely
function getEventDate(booking) {
  const s = booking.screening || {};
  const dateStr = s.show_date || booking.show_date || booking.created_at;
  const timeStr = s.start_time || booking.start_time || "00:00";

  if (!dateStr) return null;

  // Combine to ISO-like string (best effort)
  try {
    return new Date(`${dateStr}T${timeStr}`);
  } catch {
    return null;
  }
}

// render a single row
function createRow(booking) {
  const tr = document.createElement("tr");

  const s = booking.screening || {};
  const movie = (s.movie && s.movie.title) || booking.movie_title || `Movie #${booking.screening_id || booking.id}`;
  const date = s.show_date || booking.show_date || (booking.created_at ? booking.created_at.slice(0, 10) : "-");
  const time = s.start_time || booking.start_time || "--";
  const hallName = (s.hall && s.hall.name) || booking.hall_name || (s.hall_id ? `Hall ${s.hall_id}` : "N/A");
  const theatreName =
    (s.hall && s.hall.theater && s.hall.theater.name) ||
    booking.theater_name ||
    "—";

  const seats =
    booking.seats && booking.seats.length
      ? booking.seats.map((seat) => seat.seat_label || seat.code || "Seat").join(", ")
      : "—";

  const paymentStatus = (booking.payment_status || "PAID").toUpperCase();

  tr.innerHTML = `
    <td>${movie}</td>
    <td>${date}</td>
    <td>${time}</td>
    <td>${seats}</td>
    <td>${theatreName}</td>
    <td>${hallName}</td>
    <td>
      <span class="status-pill ${
        paymentStatus === "PAID" ? "status-paid" : "status-unpaid"
      }">
        ${paymentStatus}
      </span>
    </td>
  `;

  return tr;
}

function setStatus(msg) {
  const el = document.getElementById("statusMsg");
  if (!el) return;
  el.textContent = msg || "";
}

document.addEventListener("DOMContentLoaded", async () => {
  const upcomingBody = document.getElementById("upcomingBody");
  const pastBody = document.getElementById("pastBody");
  const upcomingEmpty = document.getElementById("upcomingEmpty");
  const pastEmpty = document.getElementById("pastEmpty");

  setStatus("Loading your bookings...");

  let bookings = [];
  try {
    // expects /bookings/me to return array[BookingRead]
    bookings = await coreApi.getMyBookings();
  } catch {
    setStatus("Could not load bookings. Please try again.");
    return;
  }

  if (!Array.isArray(bookings) || bookings.length === 0) {
    setStatus("");
    upcomingEmpty.classList.remove("hidden");
    pastEmpty.classList.remove("hidden");
    return;
  }

  const now = new Date();
  const upcoming = [];
  const past = [];

  bookings.forEach((b) => {
    const eventDate = getEventDate(b);
    if (eventDate && eventDate >= now) {
      upcoming.push(b);
    } else {
      past.push(b);
    }
  });

  // sort: soonest first for upcoming, newest first for past
  upcoming.sort((a, b) => {
    const da = getEventDate(a) || now;
    const db = getEventDate(b) || now;
    return da - db;
  });

  past.sort((a, b) => {
    const da = getEventDate(a) || now;
    const db = getEventDate(b) || now;
    return db - da;
  });

  // render upcoming
  if (upcoming.length === 0) {
    upcomingEmpty.classList.remove("hidden");
  } else {
    upcoming.forEach((b) => {
      upcomingBody.appendChild(createRow(b));
    });
  }

  // render past
  if (past.length === 0) {
    pastEmpty.classList.remove("hidden");
  } else {
    past.forEach((b) => {
      pastBody.appendChild(createRow(b));
    });
  }

  setStatus("");
});
