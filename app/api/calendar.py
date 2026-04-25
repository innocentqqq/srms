from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.api.auth import get_current_user, get_db
from app.models.user import User
from app.models.academic import CalendarEvent, Assignment, Exam, Subject
from app.schemas import CalendarEventCreate, CalendarEventResponse

router = APIRouter()

@router.get("/events", response_model=List[dict])
def get_calendar_events(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    events = []

    # 1. Fetch Manual Calendar Events (School-wide or Class-specific)
    query = db.query(CalendarEvent)
    if current_user.role == "student":
        # Students see global events + their class events
        query = query.filter((CalendarEvent.class_id == current_user.student.class_id) | (CalendarEvent.class_id == None))
    elif current_user.role == "teacher":
        # Teachers see global events
        query = query.filter((CalendarEvent.class_id == None)) 
    
    manual_events = query.all()
    for e in manual_events:
        events.append({
            "id": f"event_{e.id}",
            "title": e.title,
            "start": e.start_time.isoformat(),
            "end": e.end_time.isoformat(),
            "color": "#3a87ad" if e.event_type == "event" else "#f39c12",
            "extendedProps": {"description": e.description, "type": e.event_type}
        })

    # 2. Fetch Assignments (Deadlines)
    if current_user.role == "student":
        assignments = db.query(Assignment).filter(Assignment.subject_id.in_(
            [s.id for s in current_user.student.class_obj.subjects]
        )).all()
        for a in assignments:
            events.append({
                "id": f"assign_{a.id}",
                "title": f"Due: {a.title}",
                "start": a.due_date.isoformat(),
                "allDay": False,
                "color": "#e74c3c",
                "url": f"/course/{a.subject_id}",
                "extendedProps": {"type": "assignment"}
            })

    # 3. Fetch Exams
    exam_query = db.query(Exam)
    if current_user.role == "student":
        exam_query = exam_query.filter(Exam.class_id == current_user.student.class_id)
    
    exams = exam_query.all()
    for ex in exams:
        events.append({
            "id": f"exam_{ex.id}",
            "title": f"Exam: {ex.exam_name}",
            "start": ex.exam_date.isoformat(),
            "allDay": True,
            "color": "#27ae60",
            "extendedProps": {"type": "exam"}
        })

    return events

@router.post("/events", response_model=CalendarEventResponse)
def create_event(
    event: CalendarEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    db_event = CalendarEvent(
        **event.model_dump(),
        author_id=current_user.id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
