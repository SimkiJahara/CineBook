// order confirmation page

// When the page is ready, it loads the ticket data

document.addEventListener("DOMContentLoaded", function () {
  var ticketCard = document.getElementById("ticketCard");
  var noBookingSection = document.getElementById("noBooking");
  var downloadBtn = document.getElementById("downloadBtn");

  var bookingJson = localStorage.getItem("lastBooking");
  var booking = null;

  if (bookingJson) {
    booking = JSON.parse(bookingJson);
  }

  if (!booking) {
    if (ticketCard) ticketCard.classList.add("hidden");
    if (noBookingSection) noBookingSection.classList.remove("hidden");
    if (downloadBtn) downloadBtn.disabled = true;
    return;
  }

  var metaJson = localStorage.getItem("selectedScreeningMeta");
  var meta = metaJson ? JSON.parse(metaJson) : null;

  var movieEidr = localStorage.getItem("selectedMovieEidr");
  var movieTitle = "Demo Movie";
  var theaterName = "Selected theater";
  var hallName = "Selected hall";

  if (meta) {
    if (meta.theaterName) theaterName = meta.theaterName;
    if (meta.hallName) hallName = meta.hallName;
  }

  // it fills the ticket card with booking details

  function fillTicket() {
    var seats = ["A1", "A2", "A3"];
    if (booking.seats && booking.seats.length > 0) {
      seats = booking.seats.map(function (s) {
        return s.seat_label || "Seat";
      });
    }

    var created = booking.created_at
      ? new Date(booking.created_at)
      : new Date();
    var dateStr = created.toISOString().slice(0, 10);

    var ticketId = "CB-" + booking.id;
    var qrCodeText = ticketId + "-" + seats.join("-");
    var totalPaid = booking.total_price || 0;

    document.getElementById("bookingId").textContent = ticketId;
    document.getElementById("movieTitle").textContent = movieTitle;
    document.getElementById("theaterName").textContent = theaterName;
    document.getElementById("hallName").textContent = hallName;
    document.getElementById("showDate").textContent = dateStr;
    document.getElementById("seatList").textContent = seats.join(", ");
    document.getElementById("totalPaid").textContent = totalPaid;
    document.getElementById("qrText").textContent = qrCodeText;

    if (noBookingSection) noBookingSection.classList.add("hidden");
    if (ticketCard) ticketCard.classList.remove("hidden");

    if (downloadBtn) {
      downloadBtn.addEventListener("click", function () {
        console.log("Download ticket clicked (PDF not implemented).");
      });
    }
  }

  if (movieEidr) {
    coreApi
      .getMovieByEidr(movieEidr)
      .then(function (movie) {
        if (movie && movie.title) movieTitle = movie.title;
        fillTicket();
      })
      .catch(function () {
        fillTicket(); 
      });
  } else {
    fillTicket();
  }
});
