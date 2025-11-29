import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./components/LoginPage";
import RegisterPage from "./components/RegisterPage";
// Assuming you have a Dashboard or Home component for after login
// If not, we'll just redirect to LoginPage for now.
// import Dashboard from "./components/Dashboard";

function App() {
  // Placeholder state for authentication status
  // In a real app, this would be managed by Context/Redux and updated after login
  const isAuthenticated = false;

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected Routes (Example - assuming /dashboard is the main page) */}
        {/* <Route
          path="/dashboard"
          element={
            isAuthenticated ? (
              <Dashboard />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        /> */}

        {/* Default / Landing Page */}
        {/* If the user hits the root '/', they are redirected to the Login page */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* Fallback route for unknown paths */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
