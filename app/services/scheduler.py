# /app/services/scheduler.py (New File)

import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.seat import ShowSeat, SeatStatus # Adjusted import
from app.core.db import SessionLocal # Assuming this needs to be imported for standalone job
from app.services.booking_service import _fetch_and_broadcast_status # Assuming this helper exists and is needed

def release_expired_holds_job_sync():
    """
    Function for a recurrent task to release expired 'Pending' seats (Stage 3).
    This runs in a dedicated scheduler thread/process.
    """
    
    now = datetime.utcnow()
    expired_show_ids = {}

    # Open a new session for the background job
    db: Session = SessionLocal()
    
    try:
        # 1. Find all expired PENDING seats and pessimistically lock, but skip if already locked (SKIP LOCKED is critical)
        expired_seats_stmt = (
            select(ShowSeat)
            .filter(ShowSeat.status == SeatStatus.PENDING)
            .filter(ShowSeat.hold_expiry_time < now)
            .with_for_update(skip_locked=True) 
        )
        expired_seats = db.execute(expired_seats_stmt).scalars().all()

        if not expired_seats:
            return

        # 2. Update status and collect IDs for broadcasting
        for seat in expired_seats:
            seat.status = SeatStatus.AVAILABLE
            seat.reserved_by_user_id = None
            seat.hold_expiry_time = None
            
            if seat.show_id not in expired_show_ids:
                expired_show_ids[seat.show_id] = []
            expired_show_ids[seat.show_id].append(seat.id)

        db.commit()

        # 3. Broadcast the updates 
        # This part requires an explicit setup to run the async broadcast function 
        # from the sync scheduler context, typically using asyncio.run() or running
        # the whole job as an async task if using a dedicated async scheduler.
        for show_id, show_seat_ids in expired_show_ids.items():
            # In a clean environment, you would use:
            # asyncio.run(_fetch_and_broadcast_status(db, show_id, show_seat_ids))
            print(f"Scheduler: Released {len(show_seat_ids)} seats for show {show_id}.")
            
    except Exception as e:
        db.rollback()
        print(f"Error in scheduled job: {e}")
    finally:
        db.close()

# You would then integrate this function into your scheduler setup in main.py or a config file.
#