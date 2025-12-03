from fastapi import status
from app.models.booking import Seat, Booking, SeatType
from app.core.security import get_password_hash
from app.models.user import User

# Helper to create a user and get their token
def get_auth_headers(client, db_session, username="booker"):
    password = "password123"
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=get_password_hash(password),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# 1. TEST SUCCESSFUL BOOKING
def test_book_seat_success(client, db_session):
    """
    Scenario: User books an available seat.
    Expectation: 200 OK, and the seat is returned as booked.
    """
    # -- ARRANGE: Create a Seat --
    seat = Seat(row="A", number=1, seat_type=SeatType.STANDARD, price=10.0)
    db_session.add(seat)
    db_session.commit()
    
    # -- ARRANGE: Get Auth Headers --
    headers = get_auth_headers(client, db_session)

    # -- ACT --
    response = client.post(f"/api/v1/bookings/book/{seat.id}", headers=headers)

    # -- ASSERT --
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["booking"]["seat_id"] == seat.id
    assert data["booking"]["seat"]["row"] == "A"

# 2. TEST DOUBLE BOOKING (SAME SEAT)
def test_book_already_booked_seat(client, db_session):
    """
    Scenario: User A books a seat. User B tries to book the SAME seat.
    Expectation: 400 Bad Request.
    """
    # -- ARRANGE: Create Seat --
    seat = Seat(row="B", number=1, seat_type=SeatType.VIP, price=20.0)
    db_session.add(seat)
    db_session.commit()

    # -- ARRANGE: User A books the seat first --
    # We can do this directly in DB to save time, or via API
    user_a_headers = get_auth_headers(client, db_session, username="user_a")
    client.post(f"/api/v1/bookings/book/{seat.id}", headers=user_a_headers)

    # -- ACT: User B tries to book it --
    user_b_headers = get_auth_headers(client, db_session, username="user_b")
    response = client.post(f"/api/v1/bookings/book/{seat.id}", headers=user_b_headers)

    # -- ASSERT --
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already booked" in response.json()["detail"]

# 3. TEST BOOKING NON-EXISTENT SEAT
def test_book_invalid_seat(client, db_session):
    """
    Scenario: Try to book seat ID 999 which doesn't exist.
    Expectation: 400 Bad Request (or 404 depending on your API design).
    """
    headers = get_auth_headers(client, db_session)
    
    # -- ACT --
    response = client.post("/api/v1/bookings/book/999", headers=headers)

    # -- ASSERT --
    # The service returns "Seat not found" as a 400 Bad Request in your code
    assert response.status_code == status.HTTP_400_BAD_REQUEST 
    assert response.json()["detail"] == "Seat not found"