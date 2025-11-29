import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom"; // Added Link and useNavigate

// API URL is set
const API_BASE_URL = "http://localhost:8000/api/v1";

// Utility function for API calls with built-in error handling
const callLoginAPI = async (endpoint, payload) => {
  try {
    let headers = {};
    let body;

    // FIX: The FastAPI OAuth2 endpoint expects 'application/x-www-form-urlencoded' data.
    if (endpoint === "auth/token") {
      // Convert the payload object into a URLSearchParams string (form data).
      headers["Content-Type"] = "application/x-www-form-urlencoded";

      // Note: We use payload here, which is already structured correctly
      // in handleLogin (only username and password/role-related fields).
      body = new URLSearchParams(payload).toString();
    } else {
      // For all other standard API endpoints, send as JSON.
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(payload);
    }

    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      method: "POST",
      headers: headers,
      body: body, // Use the correctly formatted body
    });

    const data = await response.json();

    if (!response.ok) {
      // Ensure the error message pulls the detail field, which FastAPI uses for errors.
      throw new Error(
        data.detail || `Login failed with status ${response.status}`
      );
    }

    return data;
  } catch (error) {
    // Log the error to the console for debugging
    console.error("API Call Error:", error.message);
    throw error;
  }
};

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [selectedRole, setSelectedRole] = useState(null);
  // Using useNavigate is a good practice, even if not used yet
  const navigate = useNavigate();

  const handleLogin = async (role) => {
    setError(null);
    setSuccessMessage(null);
    setLoading(true);
    setSelectedRole(role);

    if (!email || !password) {
      setError("Email and password are required.");
      setLoading(false);
      return;
    }

    const endpoint = "auth/token";

    // FIX: FastAPI OAuth2PasswordRequestForm expects the user identifier as 'username'.
    // We pass the email as 'username' and explicitly include the 'role' as a field
    // which the FastAPI endpoint *may* extract later for role-specific authentication.
    const payload = {
      username: email, // Changed 'email' to 'username' as expected by FastAPI's OAuth2 form.
      password: password,
      // Pass the role as an extra piece of data in the form body.
      // This works because FastAPI's OAuth2PasswordRequestForm is a form dependency,
      // and additional fields can be included in the form-urlencoded body.
      role: role,
    };

    try {
      const data = await callLoginAPI(endpoint, payload);

      // Handle successful login
      setSuccessMessage(`Login successful as ${role}! Token received.`);
      console.log("Login Success Data:", data);

      // OPTIONAL TODO: Store the token (data.access_token) securely (e.g., cookies or state)
      // and redirect the user to the correct role-specific dashboard.
      // Example redirect: navigate(`/${role}/dashboard`);
    } catch (err) {
      // Set the error state from the caught error message
      setError(err.message);
    } finally {
      setLoading(false);
      setSelectedRole(null);
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
           ? "bg-cine-primary text-white hover:bg-cine-secondary" // If role is buyer
           : role === "owner" // If role is NOT buyer, check if it is owner
           ? `bg-red-800 text-white hover:bg-red-900` // If role is owner
           : `bg-neutral-800 text-white hover:bg-neutral-900` // If role is NEITHER buyer NOR owner (e.g., superadmin)
       }
    `;

  const handleKeyPress = (event, role) => {
    if (event.key === "Enter" && !loading) {
      handleLogin(role);
    }
  };

  return (
    <div
      // Using static Tailwind classes for theme colors.
      className={`min-h-screen flex items-center justify-center p-4 bg-cine-background font-sans`}
    >
      {/* Login Card Container */}
      <div
        // Using static Tailwind classes for theme colors.
        className={`w-full max-w-md p-8 space-y-8 bg-cine-surface rounded-2xl shadow-2xl shadow-red-900/50`}
      >
        <div className="text-center">
          <h2
            // Using static Tailwind classes for theme colors.
            className={`text-4xl font-extrabold text-cine-text tracking-tight`}
          >
            CineBook Login
          </h2>
          <p
            // Using static Tailwind classes for theme colors.
            className={`mt-2 text-sm text-cine-text-secondary`}
          >
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

        <form className="mt-8 space-y-6" onSubmit={(e) => e.preventDefault()}>
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
                // Using static Tailwind classes for focus rings.
                className={`appearance-none rounded-t-xl relative block w-full px-3 py-3 border border-gray-700 placeholder-gray-400 text-white bg-neutral-800 focus:outline-none focus:ring-cine-primary focus:border-cine-primary focus:z-10 sm:text-sm`}
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
                // Using static Tailwind classes for focus rings.
                className={`appearance-none rounded-b-xl relative block w-full px-3 py-3 border border-gray-700 placeholder-gray-400 text-white bg-neutral-800 focus:outline-none focus:ring-cine-primary focus:border-cine-primary focus:z-10 sm:text-sm`}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => {
                  // Allow pressing enter to log in as default role (buyer)
                  if (e.key === "Enter" && !loading) {
                    handleLogin("buyer");
                  }
                }}
                disabled={loading}
              />
            </div>
          </div>

          {/* Role Selection Buttons */}
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
              onClick={() => handleLogin("theatreowner")}
              className={getButtonClasses("owner")}
              disabled={loading && selectedRole !== "theatreowner"}
            >
              {loading && selectedRole === "theatreowner" ? (
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

          {/* Registration Link and Role Explanation */}
          <div className="flex flex-col items-center pt-4 space-y-2">
            <p className={`text-sm text-cine-text-secondary`}>
              Your role is determined by your credentials and the button you
              choose.
            </p>
            <p className={`text-sm text-cine-text-secondary`}>
              Don't have an account?
              {/* This is the key link to the registration page */}
              <Link
                to="/register"
                className="font-bold text-red-600 hover:text-red-800 ml-1 underline"
              >
                Register here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
