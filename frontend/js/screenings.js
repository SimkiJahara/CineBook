// screening Page

function getQueryParam(name) {
  var params = new URLSearchParams(window.location.search);
  return params.get(name);
}

// Initialize the screening selection page

document.addEventListener("DOMContentLoaded", function () {
  var movieEidr = getQueryParam("movie");
  var movieTitleEl = document.getElementById("selectedMovieTitle");

  if (movieEidr) {
    localStorage.setItem("selectedMovieEidr", movieEidr);
    if (movieTitleEl) {
      movieTitleEl.textContent = "Loading movie...";
    }
    coreApi
      .getMovieByEidr(movieEidr)
      .then(function (movie) {
        if (movieTitleEl) {
          movieTitleEl.textContent = movie.title || movieEidr;
        }
      })
      .catch(function (err) {
        console.error("Could not load movie", err);
        if (movieTitleEl) {
          movieTitleEl.textContent = movieEidr;
        }
      });
  } else {
    localStorage.removeItem("selectedMovieEidr");
    if (movieTitleEl) {
      movieTitleEl.textContent = "No movie selected";
    }
  }

  var citySelect = document.getElementById("citySelect");
  var theaterSelect = document.getElementById("theaterSelect");
  var hallSelect = document.getElementById("hallSelect");
  var dateInput = document.getElementById("dateInput");
  var screeningSelect = document.getElementById("screeningSelect");
  var continueBtn = document.getElementById("continueBtn");
  var selectedScreeningText = document.getElementById("selectedScreeningText");

  var selectedCityId = null;
  var selectedTheaterId = null;
  var selectedHallId = null;
  var selectedDate = "";
  var selectedScreeningId = null;

  if (dateInput) {
    var today = new Date().toISOString().split("T")[0];
    dateInput.min = today;
  }

  // Reset selects and state when it user changes city

  function resetAfterCity() {
    theaterSelect.innerHTML = '<option value="">-- Select a theater --</option>';
    hallSelect.innerHTML = '<option value="">-- Select a hall --</option>';
    screeningSelect.innerHTML = '<option value="">-- Select showtime --</option>';
    theaterSelect.disabled = true;
    hallSelect.disabled = true;
    dateInput.disabled = true;
    screeningSelect.disabled = true;
    continueBtn.disabled = true;
    selectedTheaterId = null;
    selectedHallId = null;
    selectedDate = "";
    selectedScreeningId = null;
    dateInput.value = "";
    selectedScreeningText.textContent = "None";
  }

  function resetAfterTheater() {
    hallSelect.innerHTML = '<option value="">-- Select a hall --</option>';
    screeningSelect.innerHTML = '<option value="">-- Select showtime --</option>';
    hallSelect.disabled = true;
    dateInput.disabled = true;
    screeningSelect.disabled = true;
    continueBtn.disabled = true;
    selectedHallId = null;
    selectedDate = "";
    selectedScreeningId = null;
    dateInput.value = "";
    selectedScreeningText.textContent = "None";
  }

  function resetAfterHall() {
    screeningSelect.innerHTML = '<option value="">-- Select showtime --</option>';
    screeningSelect.disabled = true;
    continueBtn.disabled = true;
    selectedDate = "";
    selectedScreeningId = null;
    dateInput.value = "";
    selectedScreeningText.textContent = "None";
  }

  coreApi
    .getCities()
    .then(function (cities) {
      cities.forEach(function (c) {
        var opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = c.name;
        citySelect.appendChild(opt);
      });
    })
    .catch(function (err) {
      console.error("Could not load cities", err);
    });

  citySelect.addEventListener("change", function (e) {
    selectedCityId = e.target.value || null;
    resetAfterCity();
    if (!selectedCityId) return;

    coreApi
      .getTheatersByCity(selectedCityId)
      .then(function (theaters) {
        theaters.forEach(function (t) {
          var opt = document.createElement("option");
          opt.value = t.id;
          opt.textContent = t.name;
          theaterSelect.appendChild(opt);
        });
        theaterSelect.disabled = false;
      })
      .catch(function (err) {
        console.error("Could not load theaters", err);
      });
  });

  theaterSelect.addEventListener("change", function (e) {
    selectedTheaterId = e.target.value || null;
    resetAfterTheater();
    if (!selectedTheaterId) return;

    coreApi
      .getHallsByTheater(selectedTheaterId)
      .then(function (halls) {
        halls.forEach(function (h) {
          var opt = document.createElement("option");
          opt.value = h.id;
          opt.textContent = h.name;
          hallSelect.appendChild(opt);
        });
        hallSelect.disabled = false;
      })
      .catch(function (err) {
        console.error("Could not load halls", err);
      });
  });

  hallSelect.addEventListener("change", function (e) {
    selectedHallId = e.target.value || null;
    resetAfterHall();
    if (!selectedHallId) {
      dateInput.disabled = true;
      return;
    }
    dateInput.disabled = false;
  });

  dateInput.addEventListener("change", function (e) {
    selectedDate = e.target.value || "";
    screeningSelect.innerHTML = '<option value="">-- Select showtime --</option>';
    screeningSelect.disabled = true;
    continueBtn.disabled = true;
    selectedScreeningId = null;
    selectedScreeningText.textContent = "None";

    if (!selectedHallId || !selectedDate) return;

    coreApi
      .getScreeningsByHallAndDate(selectedHallId, selectedDate)
      .then(function (screenings) {
        if (!screenings || screenings.length === 0) return;

        screenings.forEach(function (s) {
          var opt = document.createElement("option");
          opt.value = s.id;
          opt.textContent = s.start_time + " \u2013 " + s.base_price + " Tk";
          screeningSelect.appendChild(opt);
        });

        screeningSelect.disabled = false;
      })
      .catch(function (err) {
        console.error("Could not load screenings", err);
      });
  });

  screeningSelect.addEventListener("change", function (e) {
    selectedScreeningId = e.target.value || null;
    continueBtn.disabled = !selectedScreeningId;
    selectedScreeningText.textContent = selectedScreeningId || "None";
  });

  continueBtn.addEventListener("click", function () {
    if (!selectedScreeningId) return;

    var theaterName = "";
    if (theaterSelect.selectedIndex >= 0) {
      theaterName = theaterSelect.options[theaterSelect.selectedIndex].text;
    }

    var hallName = "";
    if (hallSelect.selectedIndex >= 0) {
      hallName = hallSelect.options[hallSelect.selectedIndex].text;
    }

    var meta = {
      cityId: selectedCityId,
      theaterId: selectedTheaterId,
      hallId: Number(selectedHallId),
      date: selectedDate,
      screeningId: Number(selectedScreeningId),
      theaterName: theaterName,
      hallName: hallName
    };

    localStorage.setItem("selectedScreeningMeta", JSON.stringify(meta));
    window.location.href = "payment.html";
  });
});
