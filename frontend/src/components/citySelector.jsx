// src/components/CitySelector.jsx

import { useEffect, useState } from "react";
import { fetchCities } from "../api/locationApi";

/**
 * Dropdown for selecting a city.
 *
 * @param {{ onCityChange?: (cityId: number | null) => void }} props
 * Optional onCityChange callback to inform parent which city is selected.
 */
function CitySelector({ onCityChange }) {
  // list of cities from backend
  const [cities, setCities] = useState([]);

  // which city is currently selected in the dropdown
  const [selectedCityId, setSelectedCityId] = useState("");

  // loading state (true while fetching)
  const [loading, setLoading] = useState(true);

  // error message (if something goes wrong)
  const [error, setError] = useState("");

  // load cities only once when component is first shown
  useEffect(() => {
    async function loadCities() {
      try {
        setLoading(true);           // we are starting the fetch
        const data = await fetchCities();  // call our API helper
        setCities(data);            // save cities to state
        setError("");               // clear any previous error
      } catch (err) {
        console.error(err);
        setError("Could not load cities.");
      } finally {
        setLoading(false);          // done loading (success or fail)
      }
    }

    loadCities();
  }, []); // [] means run this effect only once

  // when user changes the dropdown selection
  function handleChange(event) {
    const value = event.target.value;    // this is a string
    setSelectedCityId(value);            // store it locally

    if (onCityChange) {
      // if empty, send null, else send number
      const cityId = value === "" ? null : Number(value);
      onCityChange(cityId);
    }
  }

  // if still loading, show a message instead of dropdown
  if (loading) {
    return <p>Loading cities...</p>;
  }

  // if error happened, show error instead of dropdown
  if (error) {
    return <p style={{ color: "red" }}>{error}</p>;
  }

  // normal case: show dropdown
  return (
    <div style={{ marginBottom: "12px" }}>
      <label htmlFor="city-select">City: </label>
      <select
        id="city-select"
        value={selectedCityId}
        onChange={handleChange}
      >
        <option value="">-- Select a city --</option>
        {cities.map((city) => (
          <option key={city.id} value={city.id}>
            {city.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default CitySelector;
