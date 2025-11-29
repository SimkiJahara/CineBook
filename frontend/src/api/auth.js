import { API_V1_STR } from "../config";

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const AUTH_URL = `${BASE_URL}${API_V1_STR}/auth`;

export async function registerUser(username, email, password, role) {
  const response = await fetch(`${AUTH_URL}/register/${role}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
      email,
      password,
    }),
  });

  if (!response.ok) {
    // Attempt to read error message from backend
    const errorData = await response.json().catch(() => ({
      detail: `Registration failed with status: ${response.status}`,
    }));
    throw new Error(errorData.detail || "Registration failed");
  }

  return response.json();
}

// You can add loginUser, logout, etc. here later
