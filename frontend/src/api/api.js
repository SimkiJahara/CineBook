import { customAlphabet } from "nanoid";

// Note: Ensure '../config' exists and exports API_V1_STR
const API_V1_STR = "/api/v1";

// Retrieve base URL from environment variables (assuming Vite setup)
// Fallback to a common default if VITE_API_URL is not set
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const API_URL = `${API_BASE_URL}${API_V1_STR}`;

/**
 * Creates a custom alphabet for URL-safe IDs, as specified by the backend code.
 */
const nanoid = customAlphabet(
  "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
  10
);

// --- MOCK DATA GENERATION (Re-added for standalone functionality) ---

/**
 * Mocks the initial structure response based on the backend placeholder.
 */
function mockShowData(showId) {
  const rows = ["A", "B", "C", "D", "E", "F"];
  const seatsPerRow = 10;
  let showSeatIdCounter = 1;
  let physicalSeatIdCounter = 100;
  const mockSeats = [];

  rows.forEach((row_number) => {
    for (let i = 1; i <= seatsPerRow; i++) {
      let status = "Available";
      if (row_number === "D" && i >= 4 && i <= 7) {
        status = "Booked"; // Mock some already booked seats
      } else if (row_number === "E" && i === 5) {
        status = "Pending"; // Mock some temporarily held seats
      }

      mockSeats.push({
        id: showSeatIdCounter++, // ShowSeat primary key ID
        show_id: showId,
        seat_id: physicalSeatIdCounter++, // Mocking a separate physical seat ID (used by ReserveRequest)
        status: status,
        seat_number: i.toString(),
        row_number: row_number,
        reserved_by_user_id: status === "Pending" ? 10 : null, // Mock user ID (matches token payload)
        hold_expiry_time:
          status === "Pending"
            ? new Date(Date.now() + 60000).toISOString()
            : null,
      });
    }
  });

  return {
    show_id: showId,
    movie_title: `Inception: Dream Weaver - Show ${showId}`,
    layout: mockSeats,
  };
}

/**
 * Fetches initial show details and seat layout.
 * @param {number} showId The ID of the show.
 * @returns {Promise<object>} The show details and seat layout.
 */
export async function fetchShowDetails(showId) {
  try {
    // Fetch actual show metadata (even if placeholder is returned)
    const response = await fetch(`${API_URL}/shows/${showId}`);

    if (!response.ok) {
      console.warn(
        `Failed to fetch live show data from API. Using mock data for show ${showId}.`
      );
      // Fallback to mock data if API is down or doesn't return detailed structure.
      return mockShowData(showId);
    }

    const data = await response.json();

    // Merge real data with mock seat layout for visualization
    const mock = mockShowData(showId);
    return {
      ...mock, // Use mock layout structure for visualization
      ...data, // Overlay with any real metadata
    };
  } catch (error) {
    console.error("Error during show details fetch. Using mock data.", error);
    return mockShowData(showId);
  }
}

/**
 * Initiates a WebSocket connection for real-time seat status updates.
 * @param {number} showId The ID of the show.
 * @param {string} authToken The user's authentication token.
 * @param {function} onMessageCallback Callback function to handle incoming message data.
 * @returns {WebSocket} The established WebSocket connection object.
 */
export function connectSeatUpdates(showId, authToken, onMessageCallback) {
  const clientId = nanoid(); // Generate unique ID for client connection

  // Conditionally add the token to the query string (Backend will validate this)
  const tokenQuery = authToken ? `&token=${authToken}` : "";

  // WS URL structure: ws://<server_url>/api/v1/shows/ws/{show_id}?clientId=<unique_id>&token=<auth_token>
  const wsProtocol = API_BASE_URL.startsWith("https") ? "wss" : "ws";
  const wsUrl = `${wsProtocol}://${API_BASE_URL.replace(
    /^http(s?):\/\//,
    ""
  )}${API_V1_STR}/shows/ws/${showId}?clientId=${clientId}${tokenQuery}`;

  console.log(`Attempting to connect to WS: ${wsUrl}`);

  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("WebSocket connection established.");
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessageCallback(data);
    } catch (e) {
      console.error("Error parsing WebSocket message:", e, event.data);
    }
  };

  ws.onclose = (event) => {
    console.log("WebSocket connection closed.", event);
  };

  ws.onerror = (error) => {
    console.error("WebSocket error occurred:", error);
  };

  return ws;
}

/**
 * Calls the API to reserve the selected seats (Phase 1: Hold).
 * @param {number} showId The ID of the show.
 * @param {number[]} seatIds A list of physical seat IDs to hold (Seat.seatid in the schema).
 * @param {string} authToken The user's authentication token.
 * @returns {Promise<object>} The reservation response data (ReserveResponse).
 */
export async function reserveSeats(showId, seatIds, authToken) {
  const endpoint = `${API_URL}/bookings/reserve`;

  // The backend ReserveRequest expects a list of physical seat IDs (int type)
  const requestBody = {
    show_id: showId,
    seat_ids: seatIds,
  };

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify(requestBody),
  });

  if (response.status === 401) {
    throw new Error("Authentication failed. Please log in again.");
  }

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ detail: "Unknown reservation error" }));
    throw new Error(
      errorData.detail || `Reservation failed with status: ${response.status}`
    );
  }

  return response.json();
}
