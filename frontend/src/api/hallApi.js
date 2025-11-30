// src/api/hallApi.js

const API_BASE_URL = "http://127.0.0.1:8000";

// GET /halls/?theater_id=1
export async function fetchHallsByTheater(theaterId) {
    if (!theaterId) {
        return [];
    }

    const response = await fetch(
        `${API_BASE_URL}/halls/?theater_id=${theaterId}`
    );

    if (!response.ok) {
        console.error("Failed to fetch halls");
        return [];
    }

    return await response.json();
}
