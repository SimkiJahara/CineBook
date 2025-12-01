// no UI status/debug output — we keep errors in console only

// helper: get query param from URL
function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

document.addEventListener("DOMContentLoaded", async () => {
  // 0) MOVIE VIA QUERY STRING
  const movieEidr = getQueryParam("movie");
  const movieTitleEl = document.getElementById("selectedMovieTitle");

  if (movieEidr) {
    localStorage.setItem("selectedMovieEidr", movieEidr);
    try {
      movieTitleEl.textContent = "Loading movie...";
      const movie = await coreApi.getMovieByEidr(movieEidr);
      movieTitleEl.textContent = movie.title || movieEidr;
    } catch (err) {
      console.error("Could not load movie", err);
      movieTitleEl.textContent = movieEidr;
    }
  } else {
    localStorage.removeItem("selectedMovieEidr");
    movieTitleEl.textContent = "No movie selected";
  }

  // 1) DOM
  const citySelect = document.getElementById("citySelect");
  const theaterSelect = document.getElementById("theaterSelect");
  const hallSelect = document.getElementById("hallSelect");
  const dateInput = document.getElementById("dateInput");
  const screeningSelect = document.getElementById("screeningSelect");
  const continueBtn = document.getElementById("continueBtn");
  const selectedScreeningText = document.getElementById("selectedScreeningText");

  // state
  let selectedCityId = null;
  let selectedTheaterId = null;
  let selectedHallId = null;
  let selectedDate = "";
  let selectedScreeningId = null;

  // optional: lock past dates
  try {
    const today = new Date().toISOString().split("T")[0];
    dateInput.min = today;
  } catch {}

  // 2) LOAD CITIES
  try {
    const cities = await coreApi.getCities();
    cities.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.name;
      citySelect.appendChild(opt);
    });
  } catch (err) {
    console.error("Could not load cities", err);
    // quietly fail; keep control disabled behavior
    return;
  }

  // helpers to reset dependent selects
  function resetAfterCity() {
    theaterSelect.innerHTML = `<option value="">-- Select a theater --</option>`;
    hallSelect.innerHTML = `<option value="">-- Select a hall --</option>`;
    screeningSelect.innerHTML = `<option value="">-- Select showtime --</option>`;
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
    hallSelect.innerHTML = `<option value="">-- Select a hall --</option>`;
    screeningSelect.innerHTML = `<option value="">-- Select showtime --</option>`;
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
    screeningSelect.innerHTML = `<option value="">-- Select showtime --</option>`;
    screeningSelect.disabled = true;
    continueBtn.disabled = true;
    selectedDate = "";
    selectedScreeningId = null;
    dateInput.value = "";
    selectedScreeningText.textContent = "None";
  }

  // 3) CITY CHANGE
  citySelect.addEventListener("change", async (e) => {
    selectedCityId = e.target.value || null;
    resetAfterCity();
    if (!selectedCityId) return;

    try {
      const theaters = await coreApi.getTheatersByCity(selectedCityId);
      theaters.forEach((t) => {
        const opt = document.createElement("option");
        opt.value = t.id;
        opt.textContent = t.name;
        theaterSelect.appendChild(opt);
      });
      theaterSelect.disabled = false;
    } catch (err) {
      console.error("Could not load theaters", err);
    }
  });

  // 4) THEATER CHANGE
  theaterSelect.addEventListener("change", async (e) => {
    selectedTheaterId = e.target.value || null;
    resetAfterTheater();
    if (!selectedTheaterId) return;

    try {
      const halls = await coreApi.getHallsByTheater(selectedTheaterId);
      halls.forEach((h) => {
        const opt = document.createElement("option");
        opt.value = h.id;
        opt.textContent = h.name;
        hallSelect.appendChild(opt);
      });
      hallSelect.disabled = false;
    } catch (err) {
      console.error("Could not load halls", err);
    }
  });

  // 5) HALL CHANGE
  hallSelect.addEventListener("change", (e) => {
    selectedHallId = e.target.value || null;
    resetAfterHall();
    if (!selectedHallId) {
      dateInput.disabled = true;
      return;
    }
    dateInput.disabled = false;
  });

  // 6) DATE CHANGE
  dateInput.addEventListener("change", async (e) => {
    selectedDate = e.target.value || "";
    screeningSelect.innerHTML = `<option value="">-- Select showtime --</option>`;
    screeningSelect.disabled = true;
    continueBtn.disabled = true;
    selectedScreeningId = null;
    selectedScreeningText.textContent = "None";

    if (!selectedHallId || !selectedDate) return;

    try {
      const screenings = await coreApi.getScreeningsByHallAndDate(
        selectedHallId,
        selectedDate
      );

      if (!screenings.length) return;

      screenings.forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = `${s.start_time} – ${s.base_price} Tk`;
        screeningSelect.appendChild(opt);
      });

      screeningSelect.disabled = false;
    } catch (err) {
      console.error("Could not load screenings", err);
    }
  });

  // 7) SCREENING CHANGE
  screeningSelect.addEventListener("change", (e) => {
    selectedScreeningId = e.target.value || null;
    continueBtn.disabled = !selectedScreeningId;
    selectedScreeningText.textContent = selectedScreeningId || "None";
  });

  // 8) CONTINUE TO PAYMENT
  continueBtn.addEventListener("click", () => {
    if (!selectedScreeningId) return;

    const theaterName =
      theaterSelect.options[theaterSelect.selectedIndex]?.text || "";
    const hallName =
      hallSelect.options[hallSelect.selectedIndex]?.text || "";

    const meta = {
      cityId: selectedCityId,
      theaterId: selectedTheaterId,
      hallId: Number(selectedHallId),
      date: selectedDate,
      screeningId: Number(selectedScreeningId),
      theaterName,
      hallName,
    };

    localStorage.setItem("selectedScreeningMeta", JSON.stringify(meta));
    window.location.href = "payment.html";
  });
});
