// payment page

var FAKE_USER_ID = 1;
var PLATFORM_FEE = 50;

// buttons for payment types

function getSelectedPaymentMethod() {
  var radios = document.querySelectorAll('input[name="paymentMethod"]');
  var i;
  for (i = 0; i < radios.length; i++) {
    if (radios[i].checked) return radios[i].value;
  }
  return "bkash";
}

// shows a status message for the payment step

function showStatus(msg, isError) {
  var el = document.getElementById("paymentStatus");
  if (!el) return;
  el.textContent = msg || "";
  el.className = isError ? "payment-status error" : "payment-status success";
}

document.addEventListener("DOMContentLoaded", function () {
  var metaJson = localStorage.getItem("selectedScreeningMeta");
  var meta = metaJson ? JSON.parse(metaJson) : null;

  if (!meta || !meta.screeningId) {
    showStatus("No screening selected. Please go back.", true);
    return;
  }

  var screeningId = meta.screeningId;
  var hallId = meta.hallId;
  var showDate = meta.date;

  document.getElementById("theaterName").textContent = meta.theaterName;
  document.getElementById("hallName").textContent = meta.hallName;
  document.getElementById("showDate").textContent = showDate;

  coreApi
    .getScreeningsByHallAndDate(hallId, showDate)
    .then(function (list) {
      var i;
      var chosen = null;
      for (i = 0; i < list.length; i++) {
        if (list[i].id === screeningId) {
          chosen = list[i];
          break;
        }
      }

      if (!chosen) {
        showStatus("Could not load screening details.", true);
        return;
      }

      document.getElementById("showTime").textContent = chosen.start_time;

      loadMovieAndPrices(chosen);
    })
    .catch(function () {
      showStatus("Could not load screenings.", true);
    });
});

// it loads movie details  and compute prices

function loadMovieAndPrices(chosenScreening) {
  var movieEidr = localStorage.getItem("selectedMovieEidr");

  var movieTitle = "Movie";
  var movieLanguage = "-";
  var movieRating = "-";

  function fillMovieInfo() {
    document.getElementById("movieTitle").textContent = movieTitle;
    document.getElementById("movieLanguage").textContent = movieLanguage;
    document.getElementById("movieRating").textContent = movieRating;

    updatePrices(chosenScreening);
  }

  if (movieEidr) {
    coreApi
      .getMovieByEidr(movieEidr)
      .then(function (movie) {
        if (movie) {
          if (movie.title) movieTitle = movie.title;
          if (movie.language) movieLanguage = movie.language;
          if (movie.rating) movieRating = movie.rating;
        }
        fillMovieInfo();
      })
      .catch(function () {
        fillMovieInfo();
      });
  } else {
    fillMovieInfo();
  }
}

// it calculates total price

function updatePrices(chosenScreening) {
  var seats = ["A1", "A2", "A3"];
  var seatPrice = Number(chosenScreening.base_price) || 350;
  var seatCount = seats.length;
  var subTotal = seatPrice * seatCount;
  var total = subTotal + PLATFORM_FEE;

  document.getElementById("seatList").textContent = seats.join(", ");
  document.getElementById("seatCount").textContent = seatCount;
  document.getElementById("seatPrice").textContent = seatPrice;
  document.getElementById("subTotal").textContent = subTotal;
  document.getElementById("platformFee").textContent = PLATFORM_FEE;
  document.getElementById("totalAmount").textContent = total;

  initPayButton(seats, chosenScreening);
}

// for Pay button and create booking

function initPayButton(seats, chosenScreening) {
  var btn = document.getElementById("payNowBtn");
  if (!btn) return;

  btn.addEventListener("click", function () {
    btn.disabled = true;
    showStatus("Processing payment...", false);

    var payload = {
      user_id: FAKE_USER_ID,
      screening_id: chosenScreening.id,
      seats: seats,
      seat_price: Number(chosenScreening.base_price) || 350,
      payment_method: getSelectedPaymentMethod()
    };

    coreApi
      .createBooking(payload)
      .then(function (booking) {
        showStatus("Payment successful!", false);
        localStorage.setItem("lastBooking", JSON.stringify(booking));
        window.location.href = "order-confirmation.html";
      })
      .catch(function () {
        showStatus("Payment failed. Try again.", true);
      })
      .finally(function () {
        btn.disabled = false;
      });
  });
}
