// src/components/OrderConfirmationPage.jsx

import React from "react";

/*
  For now, this page can use REAL booking data if provided.

  Flow:
  - PaymentPage calls createBooking()
  - Backend returns BookingRead (id, screening_id, seats, total_price, etc.)
  - App.js stores that in lastBooking and passes as prop here: <OrderConfirmationPage booking={lastBooking} />

  We still use some fake display fields (movie name, theater, hall, time)
  because BookingRead does not include them yet.
*/

export default function OrderConfirmationPage({ booking }) {
  // Old fake ticket (used as fallback + for static fields we don't have yet)
  const fakeTicket = {
    bookingId: "CB-2025-00123",
    movie: "Haikyu",
    theater: "Star Cineplex, Bashundhara",
    hall: "Hall 3",
    date: "2025-11-11",
    time: "1:00 PM - 4:00 PM",
    seats: ["A1", "A2", "A3"],
    totalPaid: 1150, // example
    qrCodeText: "CB-2025-00123-A1-A2-A3",
  };

  const hasRealBooking = !!booking;

  // Build a ticket object that merges real data + fallback
  let ticket = fakeTicket;

  if (hasRealBooking) {
    const seatLabels =
      booking.seats && booking.seats.length
        ? booking.seats.map(
            (s) => s.seat_label || s.seat_code || "Seat"
          )
        : fakeTicket.seats;

    const createdDate = booking.created_at
      ? new Date(booking.created_at)
      : null;

    const dateStr = createdDate
      ? createdDate.toISOString().slice(0, 10) // YYYY-MM-DD
      : fakeTicket.date;

    const bookingIdText = `CB-${booking.id}`;

    ticket = {
      bookingId: bookingIdText,
      // for now, these are still fake placeholders:
      movie: fakeTicket.movie,
      theater: fakeTicket.theater,
      hall: fakeTicket.hall,
      time: fakeTicket.time,

      // real-ish data:
      date: dateStr,
      seats: seatLabels,
      totalPaid: booking.total_price || fakeTicket.totalPaid,
      qrCodeText:
        bookingIdText +
        "-" +
        seatLabels.join("-"),
    };
  }

  function handleDownload() {
    alert("Pretend downloading / saving ticket as PDF.");
  }

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "30px auto",
        padding: "24px",
        backgroundColor: "#ffffff",
        borderRadius: "14px",
        boxShadow: "0px 5px 18px rgba(0, 0, 0, 0.12)",
        fontFamily: "Segoe UI, system-ui, sans-serif",
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: "10px" }}>
        Order Confirmation
      </h2>
      <p
        style={{
          marginTop: 0,
          color: "#2c7a3f",
          fontWeight: "600",
        }}
      >
        ✅ Your ticket has been confirmed!
      </p>

      {/* Ticket container */}
      <div
        style={{
          marginTop: "20px",
          borderRadius: "12px",
          border: "1px solid #e3e3e3",
          padding: "18px",
          display: "flex",
          gap: "20px",
        }}
      >
        {/* Left side: ticket details */}
        <div style={{ flex: 2 }}>
          <p style={{ margin: 0, color: "#666" }}>Booking ID</p>
          <p
            style={{
              margin: "0 0 10px",
              fontWeight: "600",
            }}
          >
            {ticket.bookingId}
          </p>

          <h3 style={{ margin: "0 0 8px" }}>{ticket.movie}</h3>
          <p style={{ margin: "0 0 4px" }}>
            <strong>Theater:</strong> {ticket.theater}
          </p>
          <p style={{ margin: "0 0 4px" }}>
            <strong>Hall:</strong> {ticket.hall}
          </p>
          <p style={{ margin: "0 0 4px" }}>
            <strong>Date:</strong> {ticket.date}
          </p>
          <p style={{ margin: "0 0 4px" }}>
            <strong>Time:</strong> {ticket.time}
          </p>
          <p style={{ margin: "0 0 4px" }}>
            <strong>Seats:</strong> {ticket.seats.join(", ")}
          </p>
          <p style={{ margin: "10px 0 0" }}>
            <strong>Total Paid:</strong> {ticket.totalPaid} Tk
          </p>
        </div>

        {/* Right side: fake QR / code box */}
        <div
          style={{
            flex: 1,
            borderLeft: "1px dashed #ccc",
            paddingLeft: "16px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "10px",
          }}
        >
          <div
            style={{
              width: "140px",
              height: "140px",
              borderRadius: "12px",
              background:
                "repeating-linear-gradient(45deg, #333, #333 4px, #fff 4px, #fff 8px)",
            }}
          ></div>
          <p
            style={{
              fontSize: "12px",
              color: "#555",
              margin: 0,
            }}
          >
            Show this QR / code at the entrance
          </p>
          <p
            style={{
              fontSize: "11px",
              color: "#888",
              margin: 0,
            }}
          >
            {ticket.qrCodeText}
          </p>
        </div>
      </div>

      {/* Info + buttons */}
      <div style={{ marginTop: "20px" }}>
        <p style={{ fontSize: "14px", color: "#555" }}>
          A copy of this ticket has also been sent to your email / SMS
          (fake for now).
        </p>

        <button
          onClick={handleDownload}
          style={{
            marginTop: "10px",
            padding: "10px 16px",
            borderRadius: "8px",
            border: "none",
            backgroundColor: "#222",
            color: "#fff",
            fontSize: "14px",
            fontWeight: "600",
            cursor: "pointer",
          }}
        >
          Download Ticket (PDF)
        </button>
      </div>
    </div>
  );
}
