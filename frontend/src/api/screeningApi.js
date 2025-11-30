// src/api/screeningApi.js

const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Get screenings for one hall on one date.
 * Calls: GET /screenings/?hall_id=1&show_date=2025-12-01
 *
 * showDate must be in "YYYY-MM-DD" format (what <input type="date"> gives).
 */
export async function fetchScreeningsByHallAndDate(hallId, showDate) {
    if (!hallId || !showDate) {
        return [];
    }

    const params = new URLSearchParams();
    params.append("hall_id", hallId);
    params.append("show_date", showDate);

    const response = await fetch(
        `${API_BASE_URL}/screenings/?${params.toString()}`
    );

    if (!response.ok) {
        console.error("Failed to fetch screenings");
        return [];
    }

    return await response.json();
}
