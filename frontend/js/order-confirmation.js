// js/order-confirmation.js

document.addEventListener("DOMContentLoaded", async () => {
  const ticketCard = document.getElementById("ticketCard");
  const noBookingSection = document.getElementById("noBooking");
  const downloadBtn = document.getElementById("downloadBtn");

  // 1) read lastBooking from localStorage
  let booking = null;
  try {
    const json = localStorage.getItem("lastBooking");
    booking = json ? JSON.parse(json) : null;
  } catch {
    booking = null;
  }

  // No booking found → show message card instead
  if (!booking) {
    if (ticketCard) ticketCard.classList.add("hidden");
    if (noBookingSection) noBookingSection.classList.remove("hidden");
    if (downloadBtn) downloadBtn.disabled = true;
    return;
  }

  // 2) Movie + meta
  const movieEidr = localStorage.getItem("selectedMovieEidr");
  let movieTitle = "Demo Movie";
  let theaterName = "Selected theater";
  let hallName = "Selected hall";

  let meta = null;
  try {
    const json = localStorage.getItem("selectedScreeningMeta");
    meta = json ? JSON.parse(json) : null;
  } catch {
    meta = null;
  }

  if (meta) {
    theaterName = meta.theaterName || theaterName;
    hallName = meta.hallName || hallName;
  }

  if (movieEidr) {
    try {
      const movie = await coreApi.getMovieByEidr(movieEidr);
      movieTitle = movie.title || movieTitle;
    } catch {
      // ignore and keep fallback
    }
  }

  const seatLabels =
    booking.seats && booking.seats.length
      ? booking.seats.map((s) => s.seat_label || "Seat")
      : ["A1", "A2", "A3"];

  const created = booking.created_at ? new Date(booking.created_at) : new Date();
  const dateStr = created.toISOString().slice(0, 10);

  const ticketId = `CB-${booking.id}`;
  const qrCodeText = `${ticketId}-${seatLabels.join("-")}`;
  const totalPaid = booking.total_price || 0;

  // 3) fill in UI
  document.getElementById("bookingId").textContent = ticketId;
  document.getElementById("movieTitle").textContent = movieTitle;
  document.getElementById("theaterName").textContent = theaterName;
  document.getElementById("hallName").textContent = hallName;
  document.getElementById("showDate").textContent = dateStr;
  // showTime already has "See showtime selection" by default in HTML
  document.getElementById("seatList").textContent = seatLabels.join(", ");
  document.getElementById("totalPaid").textContent = totalPaid;
  document.getElementById("qrText").textContent = qrCodeText;

  if (noBookingSection) noBookingSection.classList.add("hidden");
  if (ticketCard) ticketCard.classList.remove("hidden");

  // 4) Download button (no popup)
  if (downloadBtn) {
    downloadBtn.addEventListener("click", () => {
      // No alert / popup
      // Placeholder: later you can generate real PDF here
      console.log("Download ticket clicked (PDF generation not implemented yet).");
    });
  }
});
