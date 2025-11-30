// src/components/TheaterSelector.jsx
import React, { useEffect, useState } from "react";
import { fetchTheatersByCity } from "../api/theaterApi";

/**
 * Props:
 * - cityId: selected city id (number or null)
 * - onTheaterChange: function(newTheaterId) from parent (App)
 */
function TheaterSelector({ cityId, onTheaterChange }) {
    const [theaters, setTheaters] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        // when city changes, reset selected theater and load new list
        onTheaterChange(null);
        setTheaters([]);

        if (!cityId) {
            return;
        }

        async function loadTheaters() {
            try {
                setLoading(true);
                setError("");
                const data = await fetchTheatersByCity(cityId);
                setTheaters(data);
            } catch (err) {
                console.error(err);
                setError("Could not load theaters.");
            } finally {
                setLoading(false);
            }
        }

        loadTheaters();
    }, [cityId, onTheaterChange]);

    if (!cityId) {
        return <p>Please select a city first.</p>;
    }

    return (
        <div style={{ marginTop: "16px" }}>
            <label htmlFor="theater-select">
                Theater:
            </label>{" "}
            {loading && <span>Loading...</span>}
            {error && <p style={{ color: "red" }}>{error}</p>}

            <select
                id="theater-select"
                onChange={(e) => {
                    const value = e.target.value;
                    onTheaterChange(value ? Number(value) : null);
                }}
                defaultValue=""
            >
                <option value="">-- choose a theater --</option>
                {theaters.map((t) => (
                    <option key={t.id} value={t.id}>
                        {t.name}
                    </option>
                ))}
            </select>
        </div>
    );
}

export default TheaterSelector;
