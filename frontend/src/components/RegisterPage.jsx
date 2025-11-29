// frontend/src/components/RegisterPage.jsx

import React, { useState } from "react";
import { registerUser } from "../api/auth";
import { useNavigate } from "react-router-dom";

const RegisterPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("buyer"); // Default role

  // Role-specific fields state variables
  const [fullname, setFullname] = useState(""); // For 'buyer' (maps to fullname)
  const [ownername, setOwnername] = useState(""); // For 'theatreowner' (maps to ownername)
  const [businessname, setBusinessname] = useState(""); // For 'theatreowner'
  const [licensenumber, setLicensenumber] = useState(""); // For 'theatreowner'

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    let payload = {
      email,
      password,
      role, // Pass the role to match the endpoint and schema type
    };

    if (role === "buyer") {
      // Required field for BuyerCreate is 'fullname'
      if (!fullname) {
        setError("Full Name is required for a Buyer.");
        return;
      }
      payload.fullname = fullname;
    } else if (role === "theatreowner") {
      // Required fields for TheatreOwnerCreate: businessname, ownername, licensenumber
      if (!businessname || !ownername || !licensenumber) {
        setError("All required fields must be filled for a Theatre Owner.");
        return;
      }
      payload.businessname = businessname;
      payload.ownername = ownername;
      payload.licensenumber = licensenumber;

      // Optional fields like phone, bankdetails, logourl can be added here if collected in the form
    } else {
      setError("Invalid user role selected.");
      return;
    }

    try {
      const data = await registerUser(payload);
      // Assuming the successful response contains the user's email
      setSuccess(`Registration successful! Welcome, ${data.email}.`);

      // Redirect after a short delay
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (err) {
      setError(
        err.message || "An unexpected error occurred during registration."
      );
    }
  };

  // Helper variables for dynamic form fields
  const isBuyer = role === "buyer";
  const nameValue = isBuyer ? fullname : ownername;
  const setNameChange = isBuyer ? setFullname : setOwnername;
  const nameLabel = isBuyer ? "Full Name" : "Owner Name";

  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-lg shadow-md w-full max-w-md"
      >
        <h2 className="text-2xl font-bold mb-6 text-center text-red-600">
          User Registration
        </h2>

        {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
        {success && (
          <p className="text-green-500 mb-4 text-center">{success}</p>
        )}

        {/* Role Selection */}
        <div className="mb-6">
          <label
            className="block text-gray-700 text-sm font-bold mb-2"
            htmlFor="role"
          >
            Register as
          </label>
          <select
            id="role"
            value={role}
            onChange={(e) => {
              setRole(e.target.value);
              // Clear role-specific fields when role changes to prevent sending old data
              setFullname("");
              setOwnername("");
              setBusinessname("");
              setLicensenumber("");
            }}
            className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          >
            {/* Values must match the roles used in the backend's UserRole enum and API path: 'buyer' or 'theatreowner' */}
            <option value="buyer">Buyer</option>
            <option value="theatreowner">Theatre Owner</option>
          </select>
        </div>

        {/* Email Field */}
        <div className="mb-4">
          <label
            className="block text-gray-700 text-sm font-bold mb-2"
            htmlFor="email"
          >
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>

        {/* Password Field - Note: backend enforces min_length=8 */}
        <div className="mb-6">
          <label
            className="block text-gray-700 text-sm font-bold mb-2"
            htmlFor="password"
          >
            Password (min 8 chars)
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
            required
            minLength={8}
            maxLength={70}
          />
        </div>

        {/* Dynamic Name Field (Full Name for Buyer, Owner Name for Theatre Owner) */}
        <div className="mb-4">
          <label
            className="block text-gray-700 text-sm font-bold mb-2"
            htmlFor="nameInput"
          >
            {nameLabel}
          </label>
          <input
            type="text"
            id="nameInput"
            value={nameValue}
            onChange={(e) => setNameChange(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>

        {/* Theatre Owner Specific Fields (Conditional Rendering) */}
        {!isBuyer && (
          <>
            <div className="mb-4">
              <label
                className="block text-gray-700 text-sm font-bold mb-2"
                htmlFor="businessname"
              >
                Business Name
              </label>
              <input
                type="text"
                id="businessname"
                value={businessname}
                onChange={(e) => setBusinessname(e.target.value)}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                required
              />
            </div>
            <div className="mb-6">
              <label
                className="block text-gray-700 text-sm font-bold mb-2"
                htmlFor="licensenumber"
              >
                License Number
              </label>
              <input
                type="text"
                id="licensenumber"
                value={licensenumber}
                onChange={(e) => setLicensenumber(e.target.value)}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                required
              />
            </div>
          </>
        )}

        <div className="flex items-center justify-between">
          <button
            type="submit"
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          >
            Register
          </button>
          <a
            href="/login"
            className="inline-block align-baseline font-bold text-sm text-red-600 hover:text-red-800"
          >
            Already have an account? Login
          </a>
        </div>
      </form>
    </div>
  );
};

export default RegisterPage;
