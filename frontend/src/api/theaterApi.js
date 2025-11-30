// src/api/theaterApi.js

const API_BASE_URL = "http://127.0.0.1:8000";

// GET /theaters/?city_id=1
export async function fetchTheatersByCity(cityId) {
    const response = await fetch(`${API_BASE_URL}/theaters/?city_id=${cityId}`);

    if (!response.ok) {
        console.error("Failed to fetch theaters");
        return [];
    }

    return await response.json();
}
