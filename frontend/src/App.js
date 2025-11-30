// src/App.js
import React, { useState } from "react";
import CitySelector from "./components/citySelector";
import TheaterSelector from "./components/TheaterSelector";
import HallSelector from "./components/HallSelector";
import ShowtimeSelector from "./components/ShowtimeSelector";
import MyBookingsPage from "./components/MyBookingsPage";
import PaymentPage from "./components/PaymentPage";
import OrderConfirmationPage from "./components/OrderConfirmationPage";

function App() {
    // which "page" is currently visible
    // "location" | "bookings" | "payment" | "confirmation"
    const [currentView, setCurrentView] = useState("location");

    // state used in Location & Showtime flow
    const [selectedCityId, setSelectedCityId] = useState(null);
    const [selectedTheaterId, setSelectedTheaterId] = useState(null);
    const [selectedHallId, setSelectedHallId] = useState(null);
    const [selectedScreeningId, setSelectedScreeningId] = useState(null);

    // store the last booking returned from backend after payment
    const [lastBooking, setLastBooking] = useState(null);

    return (
        <div style={{ padding: "24px", fontFamily: "sans-serif" }}>
            <h1>CineBook Frontend</h1>

            {/* Simple top navigation */}
            <div
                style={{
                    display: "flex",
                    gap: "12px",
                    margin: "16px 0 20px",
                }}
            >
                <button
                    onClick={() => setCurrentView("location")}
                    style={{
                        padding: "8px 12px",
                        borderRadius: "6px",
                        border: "1px solid #ccc",
                        backgroundColor:
                            currentView === "location" ? "#222" : "#f5f5f5",
                        color: currentView === "location" ? "#fff" : "#000",
                        cursor: "pointer",
                    }}
                >
                    Location & Showtime
                </button>

                <button
                    onClick={() => setCurrentView("bookings")}
                    style={{
                        padding: "8px 12px",
                        borderRadius: "6px",
                        border: "1px solid #ccc",
                        backgroundColor:
                            currentView === "bookings" ? "#222" : "#f5f5f5",
                        color: currentView === "bookings" ? "#fff" : "#000",
                        cursor: "pointer",
                    }}
                >
                    My Bookings
                </button>

                <button
                    onClick={() => setCurrentView("payment")}
                    style={{
                        padding: "8px 12px",
                        borderRadius: "6px",
                        border: "1px solid #ccc",
                        backgroundColor:
                            currentView === "payment" ? "#222" : "#f5f5f5",
                        color: currentView === "payment" ? "#fff" : "#000",
                        cursor: "pointer",
                    }}
                >
                    Payment
                </button>
            </div>

            {/* ====================== LOCATION & SHOWTIME ====================== */}
            {currentView === "location" && (
                <>
                    <h2>Select location and showtime</h2>

                    {/* 1. City */}
                    <CitySelector onCityChange={setSelectedCityId} />

                    {/* 2. Theater (depends on city) */}
                    <TheaterSelector
                        cityId={selectedCityId}
                        onTheaterChange={setSelectedTheaterId}
                    />

                    {/* 3. Hall (depends on theater) */}
                    <HallSelector
                        theaterId={selectedTheaterId}
                        onHallChange={setSelectedHallId}
                    />

                    {/* 4. Date + Screening (depends on hall) */}
                    <ShowtimeSelector
                        hallId={selectedHallId}
                        onScreeningChange={setSelectedScreeningId}
                    />

                    <hr style={{ marginTop: "24px" }} />

                    <h3>Debug / Preview</h3>
                    <p>Selected City ID: {selectedCityId ?? "None"}</p>
                    <p>Selected Theater ID: {selectedTheaterId ?? "None"}</p>
                    <p>Selected Hall ID: {selectedHallId ?? "None"}</p>
                    <p>Selected Screening ID: {selectedScreeningId ?? "None"}</p>
                </>
            )}

            {/* ====================== MY BOOKINGS PAGE ====================== */}
            {currentView === "bookings" && <MyBookingsPage />}

            {/* ====================== PAYMENT PAGE ====================== */}
            {currentView === "payment" && (
                <PaymentPage
                    onPaymentSuccess={(createdBooking) => {
                        // store the booking we got from backend
                        setLastBooking(createdBooking);
                        // navigate to confirmation
                        setCurrentView("confirmation");
                    }}
                />
            )}

            {/* ====================== ORDER CONFIRMATION ====================== */}
            {currentView === "confirmation" && (
                <OrderConfirmationPage booking={lastBooking} />
            )}
        </div>
    );
}

export default App;
