// src/components/HallSelector.jsx
import React, { useEffect, useState } from "react";
import { fetchHallsByTheater } from "../api/hallApi";

/**
 * Props:
 * - theaterId
 * - onHallChange(newHallId)
 */
function HallSelector({ theaterId, onHallChange }) {
    const [halls, setHalls] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        onHallChange(null);
        setHalls([]);

        if (!theaterId) {
            return;
        }

        async function loadHalls() {
            try {
                setLoading(true);
                setError("");
                const data = await fetchHallsByTheater(theaterId);
                setHalls(data);
            } catch (err) {
                console.error(err);
                setError("Could not load halls.");
            } finally {
                setLoading(false);
            }
        }

        loadHalls();
    }, [theaterId, onHallChange]);

    if (!theaterId) {
        return <p>Please select a theater first.</p>;
    }

    return (
        <div style={{ marginTop: "16px" }}>
            <label htmlFor="hall-select">
                Hall:
            </label>{" "}
            {loading && <span>Loading...</span>}
            {error && <p style={{ color: "red" }}>{error}</p>}

            <select
                id="hall-select"
                onChange={(e) => {
                    const value = e.target.value;
                    onHallChange(value ? Number(value) : null);
                }}
                defaultValue=""
            >
                <option value="">-- choose a hall --</option>
                {halls.map((h) => (
                    <option key={h.id} value={h.id}>
                        {h.name}
                    </option>
                ))}
            </select>
        </div>
    );
}

export default HallSelector;
