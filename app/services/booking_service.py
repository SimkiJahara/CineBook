# /services/booking_service.py

from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List

from app.models.seat import ShowSeat, SeatStatus, Booking, BookedSeat, Seat
from app.schemas.booking import ShowSeatResponse, BookingResponse
from app.core.websockets_manager import manager 
# from models.user import User # Import User for type hints if needed

# --- CONFIGURATION ---
HOLD_DURATION_SECONDS = 180 # 3 minutes hold time

async def _fetch_and_broadcast_status(db: Session, show_id: int, show_seat_ids: List[int]):
    """Helper to fetch fresh seat status for broadcasting."""
    
    stmt = (
        select(ShowSeat, Seat.seat_number, Seat.row_number)
        .join(Seat, ShowSeat.seat_id == Seat.id)
        .where(ShowSeat.id.in_(show_seat_ids))
    )
    
    results = db.execute(stmt).all()

    updated_seats_data = [
        ShowSeatResponse(
            id=show_seat.id,
            show_id=show_seat.show_id,
            seat_id=show_seat.seat_id,
            status=show_seat.status,
            reserved_by_user_id=show_seat.reserved_by_user_id,
            hold_expiry_time=show_seat.hold_expiry_time,
            seat_number=seat_number,
            row_number=row_number
        ).dict(by_alias=False)
        for show_seat, seat_number, row_number in results
    ]

    await manager.broadcast_seat_update(show_id, updated_seats_data)


async def reserve_seats(db: Session, show_id: int, user_id: int, seat_ids: List[int]) -> Tuple[List[ShowSeatResponse], int]:
    """
    Stage 1: Implements the two-phase commitment HOLD/PENDING logic using SELECT FOR UPDATE.
    """
    
    try:
        # 1. Find ShowSeat rows, filter by show_id and seat_id, AND lock them!
        # CRITICAL: Pessimistic Lock on the rows we intend to modify.
        seats_to_lock_stmt = (
            select(ShowSeat)
            .where(ShowSeat.show_id == show_id)
            .where(ShowSeat.seat_id.in_(seat_ids))
            .with_for_update() 
        )
        seats_to_lock = db.execute(seats_to_lock_stmt).scalars().all()

        if len(seats_to_lock) != len(seat_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="One or more seats not found for this show."
            )

        # 2. Validation and Update
        now = datetime.utcnow()
        expiry_time = now + timedelta(seconds=HOLD_DURATION_SECONDS)
        updated_show_seat_ids: List[int] = []
        unavailable_seats_detail: List[str] = []
        
        for show_seat in seats_to_lock:
            # Check for already Booked status (highest priority conflict)
            if show_seat.status == SeatStatus.BOOKED:
                unavailable_seats_detail.append(f"Seat {show_seat.seat_id} is already Booked.")
            
            # Check for active Pending hold by another user
            elif show_seat.status == SeatStatus.PENDING and show_seat.reserved_by_user_id != user_id:
                if show_seat.hold_expiry_time and show_seat.hold_expiry_time > now:
                    unavailable_seats_detail.append(f"Seat {show_seat.seat_id} is currently held by another user.")
                else:
                    # Expired lock by another user: proceed with re-reserving
                    pass
            
            # If passes checks, update the seat to PENDING status
            if show_seat.status != SeatStatus.BOOKED and show_seat.seat_id in seat_ids:
                show_seat.status = SeatStatus.PENDING
                show_seat.hold_expiry_time = expiry_time
                show_seat.reserved_by_user_id = user_id
                updated_show_seat_ids.append(show_seat.id)

        if unavailable_seats_detail:
            db.rollback() # Release the lock if validation fails
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"Some seats are unavailable: {', '.join(unavailable_seats_detail)}"
            )

        db.commit() # Release the lock and make changes visible
        
        # 3. Broadcast status update
        await _fetch_and_broadcast_status(db, show_id, updated_show_seat_ids)

        # 4. Prepare response using the committed ORM objects
        return [
            ShowSeatResponse.from_orm(s) for s in seats_to_lock if s.id in updated_show_seat_ids
        ], HOLD_DURATION_SECONDS

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during reservation: {str(e)}"
        )


async def confirm_booking(db: Session, user_id: int, show_id: int, seat_ids: List[int], payment_token: str, total_price: int) -> BookingResponse:
    """
    Stage 2: Implements the two-phase commitment CONFIRMATION logic using SELECT FOR UPDATE.
    """

    try:
        # 1. Lock the seats again for final confirmation check
        seats_to_lock_stmt = (
            select(ShowSeat)
            .where(ShowSeat.show_id == show_id)
            .where(ShowSeat.seat_id.in_(seat_ids))
            .with_for_update() # CRITICAL: Pessimistic Lock
        )
        seats_to_lock = db.execute(seats_to_lock_stmt).scalars().all()
        
        # 2. Validation: Check status, user, and expiry
        now = datetime.utcnow()
        show_seat_ids_to_confirm: List[int] = []
        seats_to_reset: List[int] = []

        for show_seat in seats_to_lock:
            if show_seat.status != SeatStatus.PENDING or show_seat.reserved_by_user_id != user_id:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail=f"Seat {show_seat.seat_id} is not reserved by you or is no longer pending."
                )
            
            if show_seat.hold_expiry_time < now:
                # Expired hold: must roll back this commit, reset the seat, and inform the user.
                seats_to_reset.append(show_seat.id)
                
                # IMPORTANT: Since we are in the transaction for the confirm request,
                # we must perform the reset now to release the lock, then commit, 
                # then raise the error.
                show_seat.status = SeatStatus.AVAILABLE
                show_seat.reserved_by_user_id = None
                show_seat.hold_expiry_time = None
            
            else:
                show_seat_ids_to_confirm.append(show_seat.id)

        if seats_to_reset:
            db.commit() # Commit the reset and release lock
            await _fetch_and_broadcast_status(db, show_id, seats_to_reset)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Seat hold for seat(s) {', '.join(map(str, seats_to_reset))} has expired. Please try again."
            )
        
        # 3. Final Commit: Update ShowSeat status to BOOKED and create Booking records
        new_booking = Booking(
            user_id=user_id,
            show_id=show_id,
            total_price=total_price,
            payment_token=payment_token,
            status=Booking.BookingStatus.CONFIRMED
        )
        db.add(new_booking)
        db.flush()

        booked_seat_objects: List[BookedSeat] = []
        for show_seat in seats_to_lock:
            # Update ShowSeat status to BOOKED
            show_seat.status = SeatStatus.BOOKED
            show_seat.hold_expiry_time = None 

            # Create the link record
            booked_seat = BookedSeat(
                booking_id=new_booking.id,
                show_seat_id=show_seat.id
            )
            booked_seat_objects.append(booked_seat)

        db.bulk_save_objects(booked_seat_objects)

        db.commit() # Final successful transaction commit
        
        # 4. Broadcast the updated seat status
        await _fetch_and_broadcast_status(db, show_id, show_seat_ids_to_confirm)

        return BookingResponse.from_orm(new_booking)

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during confirmation: {str(e)}"
        )