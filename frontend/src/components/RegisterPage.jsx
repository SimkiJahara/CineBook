// frontend/src/components/RegisterPage.jsx

import React, { useState } from "react";
import { registerUser } from "../api/auth";
import { useNavigate, Link } from "react-router-dom";

const RegisterPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("buyer");

  const [fullname, setFullname] = useState("");
  const [ownername, setOwnername] = useState("");
  const [businessname, setBusinessname] = useState("");
  const [licensenumber, setLicensenumber] = useState("");

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
      role,
    };

    if (role === "buyer") {
      if (!fullname) {
        setError("Full Name is required for a Buyer.");
        return;
      }
      payload.fullname = fullname;
    } else if (role === "theatreowner") {
      if (!businessname || !ownername || !licensenumber) {
        setError("All required fields must be filled for a Theatre Owner.");
        return;
      }
      payload.businessname = businessname;
      payload.ownername = ownername;
      payload.licensenumber = licensenumber;
    } else {
      setError("Invalid user role selected.");
      return;
    }

    try {
      const data = await registerUser(payload);
      setSuccess(`Registration successful! Welcome, ${data.email}.`);

      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (err) {
      setError(
        err.message || "An unexpected error occurred during registration."
      );
    }
  };

  const isBuyer = role === "buyer";
  const nameValue = isBuyer ? fullname : ownername;
  const setNameChange = isBuyer ? setFullname : setOwnername;
  const nameLabel = isBuyer ? "Full Name" : "Owner Name";

  const inputClasses =
    "shadow appearance-none border border-gray-700 rounded-xl w-full py-2 px-3 text-white bg-neutral-800 leading-tight focus:outline-none focus:shadow-outline focus:ring-cine-primary focus:border-cine-primary";

  return (
    <div
      // 🔑 THEME FIX: bg-cine-background REMOVED here. It is now on the <body> tag in index.html for instant theme loading.
      className="min-h-screen flex justify-center items-center p-4 font-sans"
    >
      <form
        onSubmit={handleSubmit}
        // CARD SURFACE: bg-cine-surface (Slightly Lighter Black) + Red Shadow
        className="w-full max-w-md p-8 space-y-6 bg-cine-surface rounded-2xl shadow-2xl shadow-red-900/50"
      >
        <h2 className="text-3xl font-bold mb-6 text-center text-cine-primary">
          CineBook Registration
        </h2>

        {/* Status Messages */}
        {error && (
          <p className="p-4 text-sm text-white bg-cine-primary rounded-lg mb-4 text-center">
            <span className="font-bold">Error:</span> {error}
          </p>
        )}
        {success && (
          <p className="p-4 text-sm text-green-100 bg-green-700 rounded-lg mb-4 text-center">
            <span className="font-bold">Success:</span> {success}
          </p>
        )}

        {/* Role Selection */}
        <div className="mb-6">
          <label
            className="block text-cine-text text-sm font-bold mb-2"
            htmlFor="role"
          >
            Register as
          </label>
          <select
            id="role"
            value={role}
            onChange={(e) => {
              setRole(e.target.value);
              setFullname("");
              setOwnername("");
              setBusinessname("");
              setLicensenumber("");
            }}
            className={inputClasses}
            required
          >
            <option value="buyer">Buyer</option>
            <option value="theatreowner">Theatre Owner</option>
          </select>
        </div>

        {/* Email Field */}
        <div className="mb-4">
          <label
            className="block text-cine-text text-sm font-bold mb-2"
            htmlFor="email"
          >
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={inputClasses}
            required
          />
        </div>

        {/* Password Field */}
        <div className="mb-6">
          <label
            className="block text-cine-text text-sm font-bold mb-2"
            htmlFor="password"
          >
            Password (min 8 chars)
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={inputClasses}
            required
            minLength={8}
            maxLength={70}
          />
        </div>

        {/* Dynamic Name Field */}
        <div className="mb-4">
          <label
            className="block text-cine-text text-sm font-bold mb-2"
            htmlFor="nameInput"
          >
            {nameLabel}
          </label>
          <input
            type="text"
            id="nameInput"
            value={nameValue}
            onChange={(e) => setNameChange(e.target.value)}
            className={inputClasses}
            required
          />
        </div>

        {/* Theatre Owner Specific Fields (Conditional Rendering) */}
        {!isBuyer && (
          <>
            <div className="mb-4">
              <label
                className="block text-cine-text text-sm font-bold mb-2"
                htmlFor="businessname"
              >
                Business Name
              </label>
              <input
                type="text"
                id="businessname"
                value={businessname}
                onChange={(e) => setBusinessname(e.target.value)}
                className={inputClasses}
                required
              />
            </div>
            <div className="mb-6">
              <label
                className="block text-cine-text text-sm font-bold mb-2"
                htmlFor="licensenumber"
              >
                License Number
              </label>
              <input
                type="text"
                id="licensenumber"
                value={licensenumber}
                onChange={(e) => setLicensenumber(e.target.value)}
                className={inputClasses}
                required
              />
            </div>
          </>
        )}

        <div className="flex items-center justify-between">
          <button
            type="submit"
            className="bg-cine-primary hover:bg-cine-secondary text-white font-bold py-3 px-6 rounded-xl transition duration-300 transform hover:scale-[1.02] focus:outline-none focus:shadow-outline"
          >
            Register
          </button>
          <Link
            to="/login"
            className="inline-block align-baseline font-bold text-sm text-cine-primary hover:text-cine-secondary underline"
          >
            Already have an account? Login
          </Link>
        </div>
      </form>
    </div>
  );
};

export default RegisterPage;
