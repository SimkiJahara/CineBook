import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  connectSeatUpdates,
  fetchShowDetails,
  reserveSeats,
  getUserIdFromToken, // <--- NEW IMPORT
} from "../api/api.js"; // FIXED: Added .js extension

// --- Helper Components ---

/**
 * Renders a single seat.
 */
const Seat = ({ seat, onSelect, isSelected }) => {
  // Seat status possibilities based on SeatStatus Enum from backend
  const { status, row_number, seat_number } = seat;

  let className =
    "cursor-pointer border-2 font-bold transition-colors shadow-sm";
  let tooltip = `${row_number}${seat_number}`;

  switch (status) {
    case "Available":
      className += isSelected
        ? " bg-blue-500 border-blue-600 text-white hover:bg-blue-600 shadow-blue-500/50 scale-105"
        : " bg-gray-100 border-gray-300 text-gray-800 hover:bg-green-200 hover:shadow-md";
      tooltip += isSelected ? " (Selected)" : " (Available)";
      break;
    case "Pending":
      className +=
        " bg-yellow-400 border-yellow-500 text-yellow-900 cursor-not-allowed opacity-80 shadow-inner";
      tooltip += " (Held/Pending)";
      if (seat.hold_expiry_time) {
        tooltip += ` - Expires: ${new Date(
          seat.hold_expiry_time
        ).toLocaleTimeString()}`;
      }
      break;
    case "Booked":
      className +=
        " bg-red-600 border-red-700 text-white cursor-not-allowed opacity-60";
      tooltip += " (Booked)";
      break;
    default:
      className +=
        " bg-gray-400 border-gray-500 text-gray-700 cursor-not-allowed opacity-50";
      tooltip += " (Unknown Status)";
  }

  const handleClick = () => {
    if (status === "Available") {
      onSelect(seat);
    }
  };

  return (
    <div
      className={`w-8 h-8 md:w-10 md:h-10 m-1 flex items-center justify-center rounded-lg text-xs md:text-sm ${className} transform hover:scale-105`}
      onClick={handleClick}
      title={tooltip}
    >
      {seat_number}
    </div>
  );
};

// --- Main Component ---

const SeatSelection = ({ showId, authToken }) => {
  const [seats, setSeats] = useState([]); // List of all seat objects
  const [selectedSeats, setSelectedSeats] = useState({}); // { showSeatId: seatObject }
  const [showInfo, setShowInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reservationStatus, setReservationStatus] = useState(null); // { type: 'success'|'error', message: string }
  const [holdExpiry, setHoldExpiry] = useState(null);
  const [isReserving, setIsReserving] = useState(false);

  // --- NEW: Derive currentUserId from the authToken ---
  const currentUserId = useMemo(
    () => getUserIdFromToken(authToken),
    [authToken]
  );
  // ----------------------------------------------------

  // --- Data Organization ---

  const seatsByRow = useMemo(() => {
    return seats
      .sort((a, b) => a.seat_number - b.seat_number)
      .reduce((acc, seat) => {
        const row = seat.row_number;
        if (!acc[row]) {
          acc[row] = [];
        }
        acc[row].push(seat);
        return acc;
      }, {});
  }, [seats]);

  const sortedRows = useMemo(
    () => Object.keys(seatsByRow).sort(),
    [seatsByRow]
  );

  // --- Effects and Handlers ---

  // 1. Initial Data Fetch & WebSocket Setup
  useEffect(() => {
    let ws = null;
    if (!showId) return;

    const loadData = async () => {
      setLoading(true);
      setReservationStatus(null);

      try {
        const data = await fetchShowDetails(showId);
        setShowInfo(data);
        // Initialize the seat state with the full mock/fetched layout
        setSeats(data.layout || []);

        // Establish WebSocket connection for real-time updates
        ws = connectSeatUpdates(showId, authToken, (message) => {
          if (message.event === "seat_update" && Array.isArray(message.seats)) {
            setSeats((prevSeats) => {
              const updatedSeatsMap = new Map(prevSeats.map((s) => [s.id, s]));

              message.seats.forEach((updatedSeat) => {
                updatedSeatsMap.set(updatedSeat.id, updatedSeat);

                // Logic for handling the countdown timer
                if (
                  updatedSeat.status === "Pending" &&
                  updatedSeat.hold_expiry_time &&
                  // FIXED: Use the dynamically derived ID instead of hardcoded '10'
                  updatedSeat.reserved_by_user_id === currentUserId
                ) {
                  setHoldExpiry(new Date(updatedSeat.hold_expiry_time));
                } else if (
                  updatedSeat.status !== "Pending" &&
                  prevSeats.find((s) => s.id === updatedSeat.id)?.status ===
                    "Pending"
                ) {
                  // If a seat changes from Pending (by anyone), reset the countdown if it was the reason for the timer.
                  setHoldExpiry(null);
                }
              });
              return Array.from(updatedSeatsMap.values());
            });
          }
        });
      } catch (error) {
        console.error("Initialization error:", error);
        setReservationStatus({
          type: "error",
          message: "Failed to load show data. Please refresh.",
        });
      } finally {
        setLoading(false);
      }
    };

    loadData();

    // Cleanup WebSocket on component unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [showId, authToken, currentUserId]); // ADDED: currentUserId to dependency array

  // 2. Hold Expiry Countdown Timer
  useEffect(() => {
    if (!holdExpiry) return;

    const interval = setInterval(() => {
      const now = Date.now();
      if (holdExpiry.getTime() <= now) {
        clearInterval(interval);
        setHoldExpiry(null);
        setReservationStatus({
          type: "error",
          message: "Your hold has expired. Please try again.",
        });
      } else {
        // Force component re-render every second for countdown update
        setHoldExpiry(new Date(holdExpiry));
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [holdExpiry]);

  // 3. User Seat Selection/Deselection
  const handleSelectSeat = useCallback((seat) => {
    setSelectedSeats((prev) => {
      const newSelected = { ...prev };
      // Use ShowSeat.id (unique per show) as the key for the selectedSeats map
      const key = seat.id;

      if (newSelected[key]) {
        // Deselect
        delete newSelected[key];
      } else {
        // Select only if available
        if (seat.status === "Available") {
          newSelected[key] = seat;
        }
      }
      return newSelected;
    });
  }, []);

  // 4. Handle Reservation Submission
  const handleReserve = async () => {
    if (Object.keys(selectedSeats).length === 0 || !authToken || isReserving)
      return;

    setIsReserving(true);
    setReservationStatus(null);

    // IMPORTANT: The backend API /reserve expects a list of the **physical** Seat IDs (Seat.id/seatid), not the ShowSeat IDs.
    // We are using the `seat_id` field from the ShowSeatResponse.
    const seatIdsToReserve = Object.values(selectedSeats).map((s) => s.seat_id);

    try {
      const response = await reserveSeats(showId, seatIdsToReserve, authToken);

      const expiryTime = new Date(
        Date.now() + response.hold_duration_seconds * 1000
      );
      setHoldExpiry(expiryTime);
      setReservationStatus({
        type: "success",
        message: `${response.seats.length} seats held successfully. Complete payment within the expiry time.`,
      });

      // Clear selections after successful hold
      setSelectedSeats({});
    } catch (error) {
      console.error("Reservation Error:", error);
      setReservationStatus({
        type: "error",
        message:
          error.message || "An unexpected error occurred during reservation.",
      });
    } finally {
      setIsReserving(false);
    }
  };

  // --- Render Helpers ---

  const renderSeatMap = () => {
    if (!showInfo || loading) {
      return (
        <div className="text-xl text-center p-8 text-gray-500">
          Loading show data and seat map...
        </div>
      );
    }

    return (
      <div className="flex flex-col items-center p-4">
        <div className="w-full text-center bg-gray-800 text-white p-3 rounded-t-xl shadow-lg border-b-4 border-blue-500">
          <p className="text-xl md:text-2xl font-bold tracking-wider">SCREEN</p>
        </div>
        <div className="w-4/5 h-1 bg-gray-500 mb-6 rounded-b-full shadow-xl"></div>

        <div className="overflow-x-auto w-full flex justify-center">
          <div className="flex flex-col gap-2 p-4 border border-gray-200 rounded-xl shadow-2xl bg-white min-w-max">
            {sortedRows.map((rowKey) => (
              <div key={rowKey} className="flex items-center">
                <span className="font-extrabold w-6 text-center mr-2 text-lg text-gray-700">
                  {rowKey}
                </span>
                {seatsByRow[rowKey].map((seat) => (
                  <Seat
                    key={seat.id}
                    seat={seat}
                    onSelect={handleSelectSeat}
                    isSelected={!!selectedSeats[seat.id]}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderSummary = () => {
    const count = Object.keys(selectedSeats).length;
    // Condition remains the same: user must be authenticated
    const buttonDisabled = count === 0 || isReserving || !authToken;

    let countdownDisplay = null;
    if (holdExpiry) {
      const remaining = Math.max(
        0,
        Math.floor((holdExpiry.getTime() - Date.now()) / 1000)
      );
      const minutes = Math.floor(remaining / 60);
      const seconds = remaining % 60;
      countdownDisplay = (
        <div className="text-lg font-mono text-yellow-700 bg-yellow-100 p-3 rounded-lg border border-yellow-400 animate-pulse">
          Hold expires in:{" "}
          <span className="font-bold">
            {minutes}:{seconds < 10 ? "0" : ""}
            {seconds}
          </span>
        </div>
      );
    }

    return (
      <div className="mt-8 p-6 bg-white rounded-xl shadow-3xl border-t-8 border-green-500/80">
        {countdownDisplay}

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center my-4">
          <p className="text-2xl font-bold text-gray-900 mb-2 md:mb-0">
            Selected: <span className="text-green-600">{count}</span> seat
            {count !== 1 ? "s" : ""}
          </p>
          <div className="flex flex-wrap gap-3 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 rounded bg-gray-100 border-gray-300 shadow-inner"></div>
              <span>Available</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 rounded bg-blue-500 border-blue-600 shadow-md"></div>
              <span>Selected</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 rounded bg-yellow-400 border-yellow-500"></div>
              <span>Holding</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 rounded bg-red-600 border-red-700"></div>
              <span>Booked</span>
            </div>
          </div>
        </div>

        <ul className="flex flex-wrap gap-2 mb-4 p-2 bg-gray-50 rounded-lg border border-dashed border-gray-200 min-h-10">
          {Object.values(selectedSeats).map((seat) => (
            <li
              key={seat.id}
              className="px-4 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium shadow-sm transition-all hover:bg-green-200"
            >
              <i className="fas fa-chair mr-1"></i> {seat.row_number}
              {seat.seat_number}
            </li>
          ))}
        </ul>

        {reservationStatus && (
          <div
            className={`p-3 rounded-lg mb-4 text-center border-l-4 ${
              reservationStatus.type === "success"
                ? "bg-green-100 text-green-800 border-green-600"
                : "bg-red-100 text-red-800 border-red-600"
            }`}
          >
            <p className="font-semibold">{reservationStatus.message}</p>
            {reservationStatus.type === "success" && (
              <p className="text-sm">Proceed to payment to confirm booking.</p>
            )}
          </div>
        )}

        <button
          onClick={handleReserve}
          disabled={buttonDisabled}
          className={`w-full py-3 rounded-lg text-white font-extrabold text-lg transition-all transform hover:scale-[1.01] shadow-xl 
                    ${
                      buttonDisabled
                        ? "bg-gray-400 cursor-not-allowed shadow-none"
                        : "bg-green-600 hover:bg-green-700 shadow-green-500/50"
                    }`}
        >
          {isReserving ? (
            <div className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
              Processing Reservation...
            </div>
          ) : (
            `Reserve & Proceed to Payment (${count} Seat${
              count !== 1 ? "s" : ""
            })`
          )}
        </button>
        {!authToken && (
          <p className="mt-4 text-red-500 text-center text-sm font-medium p-2 bg-red-50 rounded-lg">
            You must be logged in to reserve seats.
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-6 bg-gray-50 min-h-screen font-sans">
      <script
        src="https://kit.fontawesome.com/a076d05399.js"
        crossOrigin="anonymous"
      ></script>
      <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900 border-b pb-2 mb-2">
        {showInfo?.movie_title || `Show ${showId}`}
      </h1>
      <p className="text-lg text-gray-600 mb-8">
        Choose your seats and secure your booking!
      </p>

      {renderSeatMap()}
      {renderSummary()}
    </div>
  );
};

export default SeatSelection;
