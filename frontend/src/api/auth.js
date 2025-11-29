// frontend/src/api/auth.js

import { API_V1_STR } from "../config";

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const AUTH_URL = `${BASE_URL}${API_V1_STR}/auth`;

/**
 * Registers a new user by sending a role-specific payload to the backend.
 * @param {object} payload - The complete user object (e.g., BuyerCreate or TheatreOwnerCreate data).
 * @returns {Promise<object>} The registered user data from the backend.
 */
export async function registerUser(payload) {
  const role = payload.role; // Extract role for the URL endpoint
  const response = await fetch(`${AUTH_URL}/register/${role}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    // Send the complete payload, which matches the required Pydantic schema
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    // Attempt to read error message from backend (e.g., Pydantic validation errors)
    const errorData = await response.json().catch(() => ({
      detail: `Registration failed with status: ${response.status}`,
    }));

    // Attempt to extract the primary error detail message
    const errorMessage = errorData.detail
      ? Array.isArray(errorData.detail)
        ? errorData.detail[0]?.msg
        : errorData.detail
      : `Registration failed with status: ${response.status}`;

    throw new Error(errorMessage || "Registration failed");
  }

  // The backend should return the UserResponse object on successful registration.
  return response.json();
}

// You can add loginUser, logout, etc. here later
