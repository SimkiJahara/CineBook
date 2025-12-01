// js/payment.js

// fake user (matches MockUser in backend)
const FAKE_USER_ID = 1;
const PLATFORM_FEE = 50;

// Get selected payment method
function getSelectedPaymentMethod() {
  const radios = document.querySelectorAll('input[name="paymentMethod"]');
  for (const r of radios) {
    if (r.checked) return r.value;
  }
  return "bkash";
}

// Show payment status message
function showStatus(msg, isError = false) {
  const el = document.getElementById("paymentStatus");
  if (!el) return;
  el.textContent = msg || "";
  el.className = isError ? "payment-status error" : "payment-status success";
}

document.addEventListener("DOMContentLoaded", async () => {
  // -------------------------------
  // 1) Screening metadata from previous step
  // -------------------------------
  let meta = null;

  try {
    const metaJson = localStorage.getItem("selectedScreeningMeta");
    meta = metaJson ? JSON.parse(metaJson) : null;
  } catch {
    meta = null;
  }

  if (!meta || !meta.screeningId) {
    showStatus("No screening selected. Please go back.", true);
    return;
  }

  const screeningId = meta.screeningId;
  const hallId = meta.hallId;
  const showDate = meta.date;

  // Fill basic meta UI
  document.getElementById("theaterName").textContent = meta.theaterName;
  document.getElementById("hallName").textContent = meta.hallName;
  document.getElementById("showDate").textContent = showDate;

  // -------------------------------
  // 2) Load screening details (price + time)
  // -------------------------------
  let chosenScreening = null;

  try {
    const screenings = await coreApi.getScreeningsByHallAndDate(
      hallId,
      showDate
    );

    chosenScreening = screenings.find((s) => s.id === screeningId);

    if (!chosenScreening) {
      showStatus("Could not load screening details. Please re-select.", true);
      return;
    }

    document.getElementById("showTime").textContent =
      chosenScreening.start_time;
  } catch {
    showStatus("Error loading screening. Try again.", true);
    return;
  }

  // -------------------------------
  // 3) Load movie info
  // -------------------------------
  const movieEidr = localStorage.getItem("selectedMovieEidr");

  let movieTitle = "Movie";
  let movieLanguage = "-";
  let movieRating = "-";

  if (movieEidr) {
    try {
      const movie = await coreApi.getMovieByEidr(movieEidr);
      movieTitle = movie.title || movieTitle;
      movieLanguage = movie.language || movieLanguage;
      movieRating = movie.rating || movieRating;
    } catch {}
  }

  document.getElementById("movieTitle").textContent = movieTitle;
  document.getElementById("movieLanguage").textContent = movieLanguage;
  document.getElementById("movieRating").textContent = movieRating;

  // -------------------------------
  // 4) Fake seat selection logic
  // -------------------------------
  const selectedSeats = ["A1", "A2", "A3"];
  const seatPrice = Number(chosenScreening.base_price) || 350;
  const seatCount = selectedSeats.length;
  const subTotal = seatPrice * seatCount;
  const total = subTotal + PLATFORM_FEE;

  // Update UI
  document.getElementById("seatList").textContent =
    selectedSeats.join(", ");
  document.getElementById("seatCount").textContent = seatCount;
  document.getElementById("seatPrice").textContent = seatPrice;
  document.getElementById("subTotal").textContent = subTotal;
  document.getElementById("platformFee").textContent = PLATFORM_FEE;
  document.getElementById("totalAmount").textContent = total;

  // -------------------------------
  // 5) Pay Now button logic
  // -------------------------------
  const payBtn = document.getElementById("payNowBtn");
  if (!payBtn) return;

  payBtn.addEventListener("click", async () => {
    payBtn.disabled = true;
    showStatus("Processing payment...");

    const paymentMethod = getSelectedPaymentMethod();

    const payload = {
      user_id: FAKE_USER_ID,
      screening_id: screeningId,
      seats: selectedSeats,
      seat_price: seatPrice,
      payment_method: paymentMethod,
    };

    try {
      const booking = await coreApi.createBooking(payload);
      showStatus("Payment successful!", false);

      localStorage.setItem("lastBooking", JSON.stringify(booking));

      // go to confirmation page
      window.location.href = "order-confirmation.html";
    } catch {
      showStatus("Payment failed. Try again.", true);
    } finally {
      payBtn.disabled = false;
    }
  });
});
