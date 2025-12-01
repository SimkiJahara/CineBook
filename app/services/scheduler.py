# /app/services/scheduler.py

import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.seat import ShowSeat, SeatStatus 
# Assuming SessionLocal is available from app.core.db
# Assuming _fetch_and_broadcast_status is available from app.services.booking_service
from app.core.db import SessionLocal
from app.services.booking_service import _fetch_and_broadcast_status
from sqlalchemy.exc import OperationalError

def release_expired_holds_job_sync():
    """
    Function for a recurrent task to release expired 'Pending' seats (Stage 3).
    This function:
    1. Finds seats where the hold has expired.
    2. Uses SELECT FOR UPDATE SKIP LOCKED to acquire exclusive locks without blocking.
    3. Resets the seats to AVAILABLE.
    4. Commits the transaction.
    5. Calls the asynchronous broadcast function using asyncio.run().
    """
    
    now = datetime.utcnow()
    expired_show_ids = {}
    
    # Use the SessionLocal context to manage the session lifetime automatically
    db: Session = SessionLocal()
    
    try:
        # 1. Find and lock all expired PENDING seats
        # SKIP LOCKED is CRITICAL here to prevent the scheduler from blocking 
        # on active user transactions (reserving/confirming).
        expired_seats_stmt = (
            select(ShowSeat)
            .filter(ShowSeat.status == SeatStatus.PENDING)
            .filter(ShowSeat.hold_expiry_time < now)
            .with_for_update(skip_locked=True) 
        )
        expired_seats = db.execute(expired_seats_stmt).scalars().all()

        if not expired_seats:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Scheduler: No expired holds found.")
            return

        # 2. Update status and collect IDs for broadcasting
        for seat in expired_seats:
            seat.status = SeatStatus.AVAILABLE
            seat.reserved_by_user_id = None
            seat.hold_expiry_time = None
            
            # Group by screening_id (which is show_id in the service layer) for bulk broadcast
            if seat.screening_id not in expired_show_ids:
                expired_show_ids[seat.screening_id] = []
            expired_show_ids[seat.screening_id].append(seat.id)

        db.commit()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scheduler: Successfully released {len(expired_seats)} seat holds.")

        # 3. Broadcast the updates from the sync job context
        # We must use asyncio.run() to safely execute the async broadcast function.
        for screening_id, show_seat_ids in expired_show_ids.items():
            asyncio.run(_fetch_and_broadcast_status(db, screening_id, show_seat_ids))
            
    except OperationalError as e:
        # This catches errors like database connection issues, timeouts, etc.
        db.rollback()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scheduler Operational Error (DB Issue): {e}")
    except Exception as e:
        db.rollback()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scheduler: An unexpected error occurred: {e}")
    finally:
        db.close()