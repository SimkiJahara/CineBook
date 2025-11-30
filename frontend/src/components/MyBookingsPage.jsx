// src/components/MyBookingsPage.jsx

import React, { useEffect, useState } from "react";
import "./MyBookingsPage.css";
import { fetchMyBookings } from "../api/bookingApi";

// ===========================
// FAKE DATA (remove later)
// ===========================
const FAKE_USER = {
  name: "Simki Rahman",
  phone: "017450678",
};

const FAKE_BOOKINGS = [
  {
    id: 1,
    movie: "Haikyu",
    date: "2025-11-11",
    time: "1:00 PM - 4:00 PM",
    seats: ["1A", "2A", "3A"],
    theater: "INOX",
    hall: "3",
    payment: "PAID",
    isUpcoming: true,
  },
  {
    id: 2,
    movie: "Utshob",
    date: "2025-11-05",
    time: "4:00 PM - 7:00 PM",
    seats: ["3A", "3B", "13C"],
    theater: "Star Cineplex",
    hall: "3",
    payment: "PAID",
    isUpcoming: false,
  },
  {
    id: 3,
    movie: "Demon Slayer",
    date: "2025-12-06",
    time: "12:00 PM - 3:00 PM",
    seats: ["2A", "2B", "2C"],
    theater: "INOX",
    hall: "N/A",
    payment: "PAID",
    isUpcoming: false,
  },
];

// ===========================
// REAL BACKEND API (FOR LATER)
// ===========================
/*
import { fetchUserInfo, fetchUserBookings } from "../api/bookingApi";

useEffect(() => {
    async function loadData() {
        const user = await fetchUserInfo();
        const bookings = await fetchUserBookings();
        setUser(user);
        setBookings(bookings);
    }
    loadData();
}, []);
*/

// Helper: map backend BookingRead -> UI shape used by table
function mapApiBookingToUi(booking) {
  // created_at => date string
  const created = booking.created_at
    ? new Date(booking.created_at)
    : null;

  const dateStr = created
    ? created.toISOString().slice(0, 10) // YYYY-MM-DD
    : "N/A";

  // We don't yet have movie title / theater / hall in BookingRead,
  // so we use placeholders for now.
  const seatLabels =
    booking.seats && booking.seats.length
      ? booking.seats.map(
          (s) => s.seat_label || s.seat_code || "Seat"
        )
      : [];

  // Very rough "upcoming" logic based on created_at date
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const isUpcoming =
    created && created.setHours(0, 0, 0, 0) >= today.getTime();

  return {
    id: booking.id,
    movie: `Screening #${booking.screening_id}`,
    date: dateStr,
    time: "N/A", // we don't get showtime in BookingRead yet
    seats: seatLabels,
    theater: "N/A",
    hall: "N/A",
    payment: booking.payment_status || "PAID",
    isUpcoming,
  };
}

export default function MyBookingsPage() {
  const [user] = useState(FAKE_USER);
  const [bookings, setBookings] = useState(FAKE_BOOKINGS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 🔗 Load real bookings for the current (fake-auth) user
  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError(null);

        const apiBookings = await fetchMyBookings(); // calls /bookings/me

        if (Array.isArray(apiBookings) && apiBookings.length > 0) {
          const mapped = apiBookings.map(mapApiBookingToUi);
          setBookings(mapped);
        } else {
          // if no real bookings yet, we keep the FAKE_BOOKINGS demo data
          console.log("No real bookings yet, showing fake demo data.");
        }
      } catch (err) {
        console.error("Failed to load bookings from backend:", err);
        setError("Could not load bookings from server.");
        // fallback: keep FAKE_BOOKINGS
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const upcoming = bookings.filter((b) => b.isUpcoming);
  const past = bookings.filter((b) => !b.isUpcoming);

  return (
    <div style={{ padding: "30px" }}>
      <h1>CineBook Frontend</h1>

      {/* Navigation (placeholder) */}
      <div
        style={{
          display: "flex",
          gap: "20px",
          marginBottom: "20px",
          marginTop: "20px",
          fontWeight: "bold",
        }}
      >
        <span>SCREENINGS</span>
        <span>MOVIES</span>
        <span>THEATRES</span>
        <span>👤</span>
      </div>

      {/* Profile section */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          marginBottom: "30px",
        }}
      >
        <div
          style={{
            width: "80px",
            height: "80px",
            borderRadius: "50%",
            background: "#ddd",
            marginRight: "20px",
          }}
        ></div>

        <div>
          <p
            style={{
              margin: 0,
              fontSize: "20px",
              fontWeight: "bold",
            }}
          >
            Name: {user.name}
          </p>
          <p style={{ margin: 0, fontSize: "18px" }}>
            Phone: {user.phone}
          </p>
        </div>
      </div>

      <h2>Booking History</h2>

      {loading && <p>Loading your bookings...</p>}
      {error && (
        <p style={{ color: "red", marginTop: "8px" }}>{error}</p>
      )}

      {/* ===================== UPCOMING ===================== */}
      <h3 style={{ marginTop: "20px" }}>Upcoming</h3>
      {upcoming.length === 0 ? (
        <p>No upcoming bookings.</p>
      ) : (
        <BookingTable data={upcoming} />
      )}

      {/* ===================== PAST BOOKINGS ===================== */}
      <h3 style={{ marginTop: "30px" }}>Past History</h3>
      {past.length === 0 ? (
        <p>No previous bookings.</p>
      ) : (
        <BookingTable data={past} />
      )}
    </div>
  );
}

// ==========================
// Table component
// ==========================
function BookingTable({ data }) {
  return (
    <table
      style={{
        borderCollapse: "collapse",
        width: "100%",
        marginTop: "10px",
      }}
    >
      <thead>
        <tr>
          <TableHeader title="Movie" />
          <TableHeader title="Date" />
          <TableHeader title="Time" />
          <TableHeader title="Seat" />
          <TableHeader title="Theatre" />
          <TableHeader title="Hall" />
          <TableHeader title="Payment Status" />
        </tr>
      </thead>

      <tbody>
        {data.map((item) => (
          <tr key={item.id}>
            <TableCell>{item.movie}</TableCell>
            <TableCell>{item.date}</TableCell>
            <TableCell>{item.time}</TableCell>
            <TableCell>{item.seats.join(", ")}</TableCell>
            <TableCell>{item.theater}</TableCell>
            <TableCell>{item.hall}</TableCell>
            <TableCell
              style={{ color: "green", fontWeight: "bold" }}
            >
              {item.payment}
            </TableCell>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function TableHeader({ title }) {
  return (
    <th
      style={{
        border: "1px solid #ccc",
        padding: "8px",
        textAlign: "left",
        background: "#f5f5f5",
      }}
    >
      {title}
    </th>
  );
}

function TableCell({ children }) {
  return (
    <td style={{ border: "1px solid #ccc", padding: "8px" }}>
      {children}
    </td>
  );
}
