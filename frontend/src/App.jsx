import React, { useState, createContext, useContext } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useParams,
} from "react-router-dom";
import LoginPage from "./components/LoginPage.jsx";
import RegisterPage from "./components/RegisterPage.jsx";
import SeatSelection from "./components/SeatSelection.jsx";

// --- MOCK AUTHENTICATION SETUP ---

// NOTE: This token is a placeholder. In a real app, this is fetched from
// your FastAPI backend's /api/v1/auth/login endpoint and stored securely.
// The payload of this mock token: { sub: '1234567890', name: 'Jodie Buyer', iat: 1516239022, id: 10 }
const MOCK_AUTH_TOKEN =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvZGllIEJ1eWVyIiwiaWF0IjoxNTE2MjM5MDIyLCJpZCI6MTB9.vQhN7vLg4gA-tKK0Q_Z9F-4Qo8fQ5mG4q7r-f3Z5b2wA";
const DEFAULT_SHOW_ID = 1;

// Create Auth Context
const AuthContext = createContext(null);

// Custom Hook to use Auth Context
const useAuth = () => useContext(AuthContext);

// Auth Provider Component
const AuthProvider = ({ children }) => {
  // Setting the initial state to the mock token for immediate testing of the SeatSelection component
  const [authToken, setAuthToken] = useState(MOCK_AUTH_TOKEN);

  // Example placeholder functions for real authentication flow
  const login = (token) => setAuthToken(token);
  const logout = () => setAuthToken(null);
  const isAuthenticated = !!authToken;

  return (
    <AuthContext.Provider value={{ isAuthenticated, authToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// --- Protected Route Wrapper ---
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

// --- Show Seat Wrapper to read URL params ---
const SeatSelectionWrapper = () => {
  // Read showId from URL parameter /shows/:showId/seats
  const { showId } = useParams();
  const { authToken } = useAuth();

  // Use DEFAULT_SHOW_ID if the parameter is missing or not a number
  const parsedShowId = parseInt(showId) || DEFAULT_SHOW_ID;

  return <SeatSelection showId={parsedShowId} authToken={authToken} />;
};

// --- Main Application Component ---
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Default Route: Redirect to Seat Selection (for easy viewing/testing) */}
          <Route
            path="/"
            element={
              <Navigate to={`/shows/${DEFAULT_SHOW_ID}/seats`} replace />
            }
          />

          {/* Protected Seat Selection Route - Requires auth token for POST /reserve */}
          {/* showId is passed via URL parameter for flexibility */}
          <Route
            path="/shows/:showId/seats"
            element={
              <ProtectedRoute>
                <SeatSelectionWrapper />
              </ProtectedRoute>
            }
          />

          {/* Fallback route for unknown paths */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
