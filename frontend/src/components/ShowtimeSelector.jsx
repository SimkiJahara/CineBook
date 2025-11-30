// src/components/ShowtimeSelector.jsx
import React, { useEffect, useState } from "react";
import { fetchScreeningsByHallAndDate } from "../api/screeningApi";

/**
 * Props:
 * - hallId
 * - onScreeningChange(newScreeningId)
 */
function ShowtimeSelector({ hallId, onScreeningChange }) {
    const [date, setDate] = useState("");
    const [screenings, setScreenings] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // whenever hallId or date changes -> load screenings
    useEffect(() => {
        onScreeningChange(null);
        setScreenings([]);

        if (!hallId || !date) {
            return;
        }

        async function loadScreenings() {
            try {
                setLoading(true);
                setError("");
                const data = await fetchScreeningsByHallAndDate(hallId, date);
                setScreenings(data);
            } catch (err) {
                console.error(err);
                setError("Could not load screenings.");
            } finally {
                setLoading(false);
            }
        }

        loadScreenings();
    }, [hallId, date, onScreeningChange]);

    if (!hallId) {
        return <p>Please select a hall first.</p>;
    }

    return (
        <div style={{ marginTop: "16px" }}>
            <div>
                <label htmlFor="date-input">
                    Date:
                </label>{" "}
                <input
                    id="date-input"
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                />
            </div>

            {loading && <p>Loading screenings...</p>}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {date && screenings.length === 0 && !loading && !error && (
                <p>No screenings for this date.</p>
            )}

            {screenings.length > 0 && (
                <div style={{ marginTop: "8px" }}>
                    <label htmlFor="screening-select">
                        Showtime:
                    </label>{" "}
                    <select
                        id="screening-select"
                        onChange={(e) => {
                            const value = e.target.value;
                            onScreeningChange(value ? Number(value) : null);
                        }}
                        defaultValue=""
                    >
                        <option value="">-- choose a showtime --</option>
                        {screenings.map((s) => (
                            <option key={s.id} value={s.id}>
                                {s.start_time} – Base price: {s.base_price}
                            </option>
                        ))}
                    </select>
                </div>
            )}
        </div>
    );
}

export default ShowtimeSelector;
