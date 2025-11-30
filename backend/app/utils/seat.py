# app/utils/seat_fake.py

"""
Fake seat data generator for development.

Later:
- Replace the logic here with real database queries.
- Keep the same function names so other code does not break.
"""

from typing import List, Dict


def generate_fake_seats(screening_id: int) -> List[Dict]:
    """
    Return a list of seats for a given screening.

    For now:
    - Always generate the same layout (rows A–D, 10 seats per row).
    - Mark a few seats as 'BOOKED' just to simulate real data.

    Later:
    - You can read real seat info from the database.
    """

    # Simple fixed layout: rows A, B, C, D with 10 seats each
    rows = ["A", "B", "C", "D"]
    seats_per_row = 10

    # Fake "already booked" seats (just examples)
    # You can change this mapping for testing
    fake_booked_by_screening = {
        1: {"A1", "A2", "B5"},
        2: {"C3", "C4"},
    }

    booked_seats = fake_booked_by_screening.get(screening_id, set())

    seat_list: List[Dict] = []

    for row in rows:
        for number in range(1, seats_per_row + 1):
            code = f"{row}{number}"  # e.g. "A1", "B7"

            seat = {
                "row": row,
                "number": number,
                "code": code,
                # AVAILABLE or BOOKED for now (later you can add HOLD, BLOCKED, etc.)
                "status": "BOOKED" if code in booked_seats else "AVAILABLE",
            }

            seat_list.append(seat)

    return seat_list


def get_fake_layout_info(screening_id: int) -> Dict:
    """
    Small helper to return layout + metadata.

    This is useful if frontend wants both:
    - list of seats
    - how many rows, seats per row

    For now, everything is hardcoded.
    """

    seats = generate_fake_seats(screening_id)

    layout_info = {
        "screening_id": screening_id,
        "rows": sorted({s["row"] for s in seats}),
        "seats_per_row": max(s["number"] for s in seats) if seats else 0,
        "seats": seats,
    }

    return layout_info
