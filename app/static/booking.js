// =============================================================================
// Movie Ticket Booking - Frontend JavaScript
// =============================================================================
// Handles seat display, booking actions, and JWT token management
// =============================================================================

const API_BASE = '/api/v1/bookings';

// =============================================================================
// Token Management (reusing from existing auth system)
// =============================================================================

function getToken() {
    return localStorage.getItem('access_token');
}

function removeToken() {
    localStorage.removeItem('access_token');
}

function isAuthenticated() {
    return !!getToken();
}

// =============================================================================
// API Request Helper
// =============================================================================

async function apiRequest(endpoint, options = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    const token = getToken();
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(endpoint, config);
        
        if (response.status === 401) {
            // Token expired or invalid
            removeToken();
            showToast('Session expired. Please login again.', 'error');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
            return null;
        }

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// =============================================================================
// UI Helpers
// =============================================================================

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function updateAuthUI() {
    const userSection = document.getElementById('userSection');
    const authSection = document.getElementById('authSection');
    const myBookingsSection = document.getElementById('myBookingsSection');

    if (isAuthenticated()) {
        userSection.style.display = 'flex';
        authSection.style.display = 'none';
        myBookingsSection.style.display = 'block';
        loadUserInfo();
        loadMyBookings();
    } else {
        userSection.style.display = 'none';
        authSection.style.display = 'flex';
        myBookingsSection.style.display = 'none';
    }
}

async function loadUserInfo() {
    try {
        const user = await apiRequest('/api/v1/users/me');
        if (user) {
            document.getElementById('userGreeting').textContent = `Hello, ${user.full_name || user.username}!`;
        }
    } catch (error) {
        console.error('Failed to load user info:', error);
    }
}

// =============================================================================
// Theater & Seat Management
// =============================================================================

async function loadTheater() {
    const theaterGrid = document.getElementById('theaterGrid');
    
    try {
        const data = await apiRequest(`${API_BASE}/seats`);
        
        if (!data || !data.seats || data.seats.length === 0) {
            theaterGrid.innerHTML = '<div class="loading">No seats available. Please run setup_db.py to initialize seats.</div>';
            return;
        }

        // Update stats
        document.getElementById('totalSeats').textContent = data.total_seats;
        document.getElementById('availableSeats').textContent = data.available_seats;
        document.getElementById('bookedSeats').textContent = data.booked_seats;

        // Group seats by row
        const seatsByRow = {};
        data.seats.forEach(seat => {
            if (!seatsByRow[seat.row]) {
                seatsByRow[seat.row] = [];
            }
            seatsByRow[seat.row].push(seat);
        });

        // Sort rows alphabetically
        const sortedRows = Object.keys(seatsByRow).sort();

        // Build theater HTML
        let theaterHTML = '';
        
        sortedRows.forEach(row => {
            const seats = seatsByRow[row].sort((a, b) => a.number - b.number);
            
            theaterHTML += `
                <div class="seat-row">
                    <span class="row-label">${row}</span>
                    <div class="seats">
            `;
            
            seats.forEach(seat => {
                const statusClass = seat.booked_by_current_user 
                    ? 'mine' 
                    : (seat.is_booked ? 'booked' : 'available');
                const typeClass = seat.seat_type;
                const clickable = !seat.is_booked || seat.booked_by_current_user;
                const onClick = clickable 
                    ? `onclick="handleSeatClick(${seat.id}, ${seat.is_booked}, ${seat.booked_by_current_user})"` 
                    : '';
                
                theaterHTML += `
                    <div class="seat ${statusClass} ${typeClass}" 
                         ${onClick}
                         title="${seat.seat_type.toUpperCase()} - ${seat.price} Taka${seat.is_booked ? ' (Booked)' : ''}">
                        ${seat.number}
                    </div>
                `;
            });
            
            theaterHTML += `
                    </div>
                </div>
            `;
        });

        theaterGrid.innerHTML = theaterHTML;
        
    } catch (error) {
        theaterGrid.innerHTML = `<div class="loading">Failed to load seats: ${error.message}</div>`;
    }
}

async function handleSeatClick(seatId, isBooked, isMyBooking) {
    if (!isAuthenticated()) {
        showToast('Please login to book seats', 'error');
        setTimeout(() => {
            window.location.href = '/';
        }, 1500);
        return;
    }

    if (isMyBooking) {
        // Show option to cancel
        if (confirm('Do you want to cancel this booking?')) {
            await cancelBooking(seatId);
        }
        return;
    }

    if (isBooked) {
        showToast('This seat is already booked', 'error');
        return;
    }

    // Book the seat
    await bookSeat(seatId);
}

async function bookSeat(seatId) {
    try {
        const result = await apiRequest(`${API_BASE}/book/${seatId}`, {
            method: 'POST',
        });

        if (result && result.success) {
            showToast(result.message, 'success');
            // Reload theater to show updated status
            await loadTheater();
            await loadMyBookings();
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function cancelBooking(seatId) {
    try {
        // First get my bookings to find the booking ID for this seat
        const bookings = await apiRequest(`${API_BASE}/my-bookings`);
        const booking = bookings.find(b => b.seat_id === seatId);
        
        if (!booking) {
            showToast('Booking not found', 'error');
            return;
        }

        const result = await apiRequest(`${API_BASE}/cancel/${booking.id}`, {
            method: 'DELETE',
        });

        if (result && result.success) {
            showToast(result.message, 'success');
            await loadTheater();
            await loadMyBookings();
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// =============================================================================
// My Bookings
// =============================================================================

async function loadMyBookings() {
    if (!isAuthenticated()) return;

    const bookingsList = document.getElementById('myBookingsList');
    
    try {
        const bookings = await apiRequest(`${API_BASE}/my-bookings`);
        
        if (!bookings || bookings.length === 0) {
            bookingsList.innerHTML = '<div class="no-bookings">You have no bookings yet.</div>';
            return;
        }

        let html = '';
        let totalPrice = 0;
        
        bookings.forEach(booking => {
            totalPrice += booking.seat.price;
            const bookedAt = new Date(booking.booked_at).toLocaleString();
            
            html += `
                <div class="booking-item">
                    <div class="booking-info">
                        <span class="booking-seat">Seat ${booking.seat.row}${booking.seat.number}</span>
                        <span class="booking-details">
                            ${booking.seat.seat_type.toUpperCase()} - ${booking.seat.price} Taka | 
                            Booked: ${bookedAt}
                        </span>
                    </div>
                    <button class="btn btn-danger btn-sm" onclick="cancelBookingById(${booking.id})">
                        Cancel
                    </button>
                </div>
            `;
        });

        html += `
            <div class="booking-item" style="background-color: var(--accent-primary); margin-top: 1rem;">
                <div class="booking-info">
                    <span class="booking-seat">Total: ${bookings.length} seat(s)</span>
                    <span class="booking-details" style="color: white;">Amount: ${totalPrice} Taka</span>
                </div>
            </div>
        `;

        bookingsList.innerHTML = html;
        
    } catch (error) {
        bookingsList.innerHTML = `<div class="no-bookings">Failed to load bookings: ${error.message}</div>`;
    }
}

async function cancelBookingById(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking?')) return;

    try {
        const result = await apiRequest(`${API_BASE}/cancel/${bookingId}`, {
            method: 'DELETE',
        });

        if (result && result.success) {
            showToast(result.message, 'success');
            await loadTheater();
            await loadMyBookings();
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// =============================================================================
// Navigation
// =============================================================================

function goToDashboard() {
    window.location.href = '/dashboard';
}

function logout() {
    removeToken();
    showToast('Logged out successfully', 'success');
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

// =============================================================================
// Initialize
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI();
    loadTheater();
});
