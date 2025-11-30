// src/api/bookingApi.js

const API_BASE_URL = "http://127.0.0.1:8000";

// Helper to build headers with optional auth
function buildHeaders() {
  const headers = {
    "Content-Type": "application/json",
  };

  const token = localStorage.getItem("authToken");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return headers;
}

// -----------------------------
// CREATE BOOKING (POST /bookings/)
// -----------------------------
export async function createBooking(bookingInput) {
  const response = await fetch(`${API_BASE_URL}/bookings/`, {
    method: "POST",
    headers: buildHeaders(),
    body: JSON.stringify(bookingInput),
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(
      `Booking failed with status ${response.status}: ${errText}`
    );
  }

  return await response.json();
}

// -----------------------------
// FETCH BOOKINGS FOR CURRENT USER (GET /bookings/me)
// -----------------------------
export async function fetchMyBookings() {
  const response = await fetch(`${API_BASE_URL}/bookings/me`, {
    method: "GET",
    headers: buildHeaders(),
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(
      `Fetching bookings failed with status ${response.status}: ${errText}`
    );
  }

  return await response.json();
}
