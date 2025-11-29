import React, { useState } from "react";
// Assuming you have defined your FastAPI backend URL (e.g., running on http://localhost:8000)
// Replace this with your actual backend host when deploying
const API_BASE_URL = "http://localhost:8000/api/v1";

// Utility function for API calls with built-in error handling
const callLoginAPI = async (endpoint, payload) => {
  try {
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    // Check for HTTP errors (e.g., 401 Unauthorized, 404 Not Found, 500 Internal Error)
    if (!response.ok) {
      // Throw the error message from the backend, or a generic message if none
      throw new Error(
        data.detail || `Login failed with status ${response.status}`
      );
    }

    // Return the successful response data
    return data;
  } catch (error) {
    console.error("API Call Error:", error.message);
    // Re-throw the error to be handled by the component's state update logic
    throw error;
  }
};

// --- Custom Theme Colors for Cinebook (Updated to Red & Black) ---
const colors = {
  primary: "#E50914", // Vibrant Cinema Red for main actions (e.g., Netflix red)
  secondary: "#B80010", // Darker Red for accents or secondary buttons
  background: "#0A0A0A", // Deep Black for the overall screen
  surface: "#1C1C1C", // Slightly lighter black for the card/form area
  text: "#FFFFFF", // White for primary text
  textSecondary: "#AAAAAA", // Light grey for hints/labels
};

const LoginPage = () => {
  // State to hold user input for login
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  // State for UI feedback
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [selectedRole, setSelectedRole] = useState(null); // Tracks which role button was clicked

  /**
   * Handles the form submission and initiates the login process.
   * @param {string} role - The intended user role (buyer, owner, superadmin).
   */
  const handleLogin = async (role) => {
    // Clear previous state
    setError(null);
    setSuccessMessage(null);
    setLoading(true);
    setSelectedRole(role); // Highlight the button being used

    // Basic client-side validation
    if (!email || !password) {
      setError("Email and password are required.");
      setLoading(false);
      return;
    }

    const endpoint = "auth/token"; // Endpoint for the OAuth2 login flow

    // NOTE: FastAPI's OAuth2PasswordRequestForm expects data in 'application/x-www-form-urlencoded' format.
    // However, since we are sending JSON with email/password/role here, your FastAPI endpoint
    // needs to be adjusted to accept JSON or you need to send form data.
    // We will stick to JSON for simplicity on the frontend and assume the backend is adjusted.
    const payload = {
      email: email,
      password: password,
      role: role,
    };

    try {
      const data = await callLoginAPI(endpoint, payload);

      // On successful login
      setSuccessMessage(`Login successful as ${role}! Token received.`);
      // In a real application, you would store the token (data.access_token)
      // in localStorage or a secure cookie and redirect the user.

      // SIMULATION: Log the received token/data for demonstration
      console.log("Login Success Data:", data);
    } catch (err) {
      // Error handling from the API utility function
      setError(err.message);
    } finally {
      setLoading(false);
      setSelectedRole(null); // Reset role highlight
    }
  };

  // Tailwind CSS classes for the primary action buttons
  const getButtonClasses = (role) => `
        w-full py-3 px-6 text-lg font-bold transition duration-300 transform
        rounded-xl shadow-lg
        ${
          loading && selectedRole === role
            ? "bg-gray-700 text-gray-500 cursor-not-allowed" // Loading state (darker)
            : "hover:scale-[1.02] hover:shadow-xl" // Hover state
        }
        ${
          role === "buyer"
            ? `bg-[${colors.primary}] text-white hover:bg-[${colors.secondary}]` // Strong Red
            : role === "owner"
            ? `bg-red-800 text-white hover:bg-red-900` // Muted Red/Maroon
            : `bg-neutral-800 text-white hover:bg-neutral-900` // Dark Grey/Black for Superadmin
        }
    `;

  // Function to handle the Enter key press in input fields
  const handleKeyPress = (event, role) => {
    if (event.key === "Enter" && !loading) {
      handleLogin(role);
    }
  };

  return (
    <div
      className={`min-h-screen flex items-center justify-center p-4 bg-[${colors.background}] font-sans`}
    >
      {/* Login Card Container */}
      <div
        className={`w-full max-w-md p-8 space-y-8 bg-[${colors.surface}] rounded-2xl shadow-2xl shadow-red-900/50`}
      >
        <div className="text-center">
          <h2
            className={`text-4xl font-extrabold text-[${colors.text}] tracking-tight`}
          >
            CineBook Login
          </h2>
          <p className={`mt-2 text-sm text-[${colors.textSecondary}]`}>
            Enter your credentials and select your role
          </p>
        </div>

        {/* Status Messages */}
        {error && (
          <div
            className="p-4 text-sm text-red-100 bg-red-600 rounded-lg"
            role="alert"
          >
            <span className="font-medium">Error:</span> {error}
          </div>
        )}
        {successMessage && (
          <div
            className="p-4 text-sm text-green-100 bg-green-700 rounded-lg"
            role="alert"
          >
            <span className="font-medium">Success:</span> {successMessage}
          </div>
        )}

        <form className="mt-8 space-y-6">
          {/* Email Input */}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email-address" className={`sr-only`}>
                Email address
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                // Note: Input background is changed to dark neutral for better contrast
                className={`appearance-none rounded-t-xl relative block w-full px-3 py-3 border border-gray-700 placeholder-gray-400 text-white bg-neutral-800 focus:outline-none focus:ring-[${colors.primary}] focus:border-[${colors.primary}] focus:z-10 sm:text-sm`}
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
              />
            </div>
            {/* Password Input */}
            <div>
              <label htmlFor="password" className={`sr-only`}>
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                // Note: Input background is changed to dark neutral for better contrast
                className={`appearance-none rounded-b-xl relative block w-full px-3 py-3 border border-gray-700 placeholder-gray-400 text-white bg-neutral-800 focus:outline-none focus:ring-[${colors.primary}] focus:border-[${colors.primary}] focus:z-10 sm:text-sm`}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => handleKeyPress(e, "buyer")}
                disabled={loading}
              />
            </div>
          </div>

          {/* Role Selection Buttons (Red & Black Theme) */}
          <div className="space-y-4 pt-4">
            <button
              type="button"
              onClick={() => handleLogin("buyer")}
              className={getButtonClasses("buyer")}
              disabled={loading && selectedRole !== "buyer"}
            >
              {loading && selectedRole === "buyer" ? (
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              ) : (
                "Login as Buyer"
              )}
            </button>

            <button
              type="button"
              onClick={() => handleLogin("owner")}
              className={getButtonClasses("owner")}
              disabled={loading && selectedRole !== "owner"}
            >
              {loading && selectedRole === "owner" ? (
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              ) : (
                "Login as Theatre Owner"
              )}
            </button>

            <button
              type="button"
              onClick={() => handleLogin("superadmin")}
              className={getButtonClasses("superadmin")}
              disabled={loading && selectedRole !== "superadmin"}
            >
              {loading && selectedRole === "superadmin" ? (
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              ) : (
                "Login as Superadmin"
              )}
            </button>
          </div>

          <div
            className={`text-center pt-4 text-[${colors.textSecondary}] text-sm`}
          >
            <p>
              Your role is determined by your credentials and the button you
              choose.
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
