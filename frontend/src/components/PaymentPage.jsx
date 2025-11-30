// src/components/PaymentPage.jsx

import React, { useState, useEffect } from "react";
import { createBooking } from "../api/bookingApi";
import { movieApi } from "../api/movie_api";

/*
  CURRENT STATUS (very important to understand):

  - Booking flow is REAL:
      -> PaymentPage calls POST /bookings with:
         { user_id, screening_id, seats, seat_price, payment_method }
      -> Backend creates booking + three seats (A1, A2, A3).

  - Seat selection is FAKE (default 3 seats).
  - Login is FAKE (we will treat "user_id = 1" as the logged-in user for now).

  - In this file we now ALSO call the REAL movies backend:
      -> GET /api/movies/discovery/now-showing?limit=1
      -> Use that movie's title (and later, poster, etc.) in the UI.

  Later, when:
    - real login is ready → replace user_id=1 with real current user
    - real seat selection is ready → pass real seats instead of hardcoded
    - screening is linked to movie.eidr → fetch the correct movie for that screening
*/

export default function PaymentPage({ onPaymentSuccess }) {
  // =====================
  // 1) "Logged in" user
  // =====================
  // For now, this is our fake logged-in user ID
  const userId = 1;

  // =====================
  // 2) Movie from backend
  // =====================
  const [movie, setMovie] = useState(null);
  const [movieLoading, setMovieLoading] = useState(true);
  const [movieError, setMovieError] = useState(null);

  useEffect(() => {
    async function loadMovie() {
      try {
        setMovieLoading(true);
        setMovieError(null);

        // 🔥 Real call to teammate's backend:
        // GET /api/movies/discovery/now-showing?limit=1
        const movies = await movieApi.getNowShowing(1);

        // If there is at least one movie, use it
        if (movies && movies.length > 0) {
          setMovie(movies[0]);
        } else {
          setMovie(null);
        }
      } catch (err) {
        console.error("Failed to load movie:", err);
        setMovieError("Could not load movie from backend.");
        setMovie(null);
      } finally {
        setMovieLoading(false);
      }
    }

    loadMovie();
  }, []);

  // =====================
  // 3) Fake screening / seat info
  // =====================
  // These parts will later come from:
  //  - your Location & Showtime flow (selected screening, hall, date, time)
  //  - real seat-selection component (chosen seats)
  const fakeScreening = {
    theater: "Star Cineplex, Bashundhara",
    hall: "Hall 3",
    date: "2025-11-11",
    time: "1:00 PM - 4:00 PM",
    seats: ["A1", "A2", "A3"],
    pricePerSeat: 350,
    screeningId: 2, // <- your real screening id will come here later
  };

  const totalSeats = fakeScreening.seats.length;
  const subtotal = fakeScreening.pricePerSeat * totalSeats;
  const platformFee = 50;
  const total = subtotal + platformFee;

  // =====================
  // 4) Payment state
  // =====================
  const [paymentMethod, setPaymentMethod] = useState("bkash");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // ==========================
  // 5) Pay Now -> createBooking()
  // ==========================
  async function handlePayNow() {
    if (isSubmitting) return;

    try {
      setIsSubmitting(true);

      // 🔥 This object matches BookingCreate schema
      const bookingInput = {
        user_id: userId,
        screening_id: fakeScreening.screeningId,
        seats: fakeScreening.seats,
        seat_price: fakeScreening.pricePerSeat,
        payment_method: paymentMethod,
      };

      const createdBooking = await createBooking(bookingInput);

      if (onPaymentSuccess) {
        onPaymentSuccess(createdBooking);
      }
    } catch (err) {
      console.error(err);
      alert("Payment / booking failed. See console for details.");
    } finally {
      setIsSubmitting(false);
    }
  }

  // Choose movie title (real if possible, fallback otherwise)
  const movieTitle = movie?.title || "Demo Movie";
  const movieLanguage = movie?.language || "English";
  const movieRating = movie?.rating || "Not Rated";

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "30px auto",
        padding: "24px",
        borderRadius: "12px",
        backgroundColor: "white",
        boxShadow: "0px 4px 12px rgba(0,0,0,0.1)",
        fontFamily: "Segoe UI, sans-serif",
      }}
    >
      <h2 style={{ marginBottom: "16px" }}>Payment</h2>

      {/* ============ MOVIE LOADING STATE ============ */}
      {movieLoading && <p>Loading movie info...</p>}
      {movieError && (
        <p style={{ color: "red", marginBottom: "8px" }}>{movieError}</p>
      )}

      {/* Booking summary box */}
      <div
        style={{
          border: "1px solid #eee",
          borderRadius: "10px",
          padding: "16px",
          marginBottom: "20px",
          backgroundColor: "#fafafa",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Booking Summary</h3>

        <p>
          <strong>Movie:</strong> {movieTitle}
        </p>

        {/* You can show more real movie data later */}
        <p>
          <strong>Language:</strong> {movieLanguage}
        </p>
        <p>
          <strong>Rating:</strong> {movieRating}
        </p>

        <p>
          <strong>Theater:</strong> {fakeScreening.theater}
        </p>
        <p>
          <strong>Hall:</strong> {fakeScreening.hall}
        </p>
        <p>
          <strong>Date:</strong> {fakeScreening.date}
        </p>
        <p>
          <strong>Time:</strong> {fakeScreening.time}
        </p>
        <p>
          <strong>Seats:</strong> {fakeScreening.seats.join(", ")} (
          {totalSeats} seats)
        </p>
      </div>

      {/* Price details */}
      <div
        style={{
          border: "1px solid #eee",
          borderRadius: "10px",
          padding: "16px",
          marginBottom: "20px",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Price Details</h3>
        <p>
          Ticket price ({totalSeats} x {fakeScreening.pricePerSeat} Tk):{" "}
          <strong>{subtotal} Tk</strong>
        </p>
        <p>
          Platform fee: <strong>{platformFee} Tk</strong>
        </p>
        <hr />
        <p>
          <strong>Total:</strong> {total} Tk
        </p>
      </div>

      {/* Payment method selection */}
      <div
        style={{
          border: "1px solid #eee",
          borderRadius: "10px",
          padding: "16px",
          marginBottom: "20px",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Select Payment Method</h3>

        <label style={{ display: "block", marginBottom: "8px" }}>
          <input
            type="radio"
            name="payment"
            value="bkash"
            checked={paymentMethod === "bkash"}
            onChange={(e) => setPaymentMethod(e.target.value)}
          />{" "}
          bKash
        </label>

        <label style={{ display: "block", marginBottom: "8px" }}>
          <input
            type="radio"
            name="payment"
            value="nagad"
            checked={paymentMethod === "nagad"}
            onChange={(e) => setPaymentMethod(e.target.value)}
          />{" "}
          Nagad
        </label>

        <label style={{ display: "block", marginBottom: "8px" }}>
          <input
            type="radio"
            name="payment"
            value="card"
            checked={paymentMethod === "card"}
            onChange={(e) => setPaymentMethod(e.target.value)}
          />{" "}
          Credit / Debit Card
        </label>
      </div>

      <button
        onClick={handlePayNow}
        disabled={isSubmitting}
        style={{
          padding: "12px 20px",
          borderRadius: "8px",
          border: "none",
          backgroundColor: isSubmitting ? "#777" : "#222",
          color: "white",
          fontSize: "16px",
          cursor: isSubmitting ? "default" : "pointer",
        }}
      >
        {isSubmitting ? "Processing..." : `Pay Now (${total} Tk)`}
      </button>
    </div>
  );
}
