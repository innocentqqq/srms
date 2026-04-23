from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.academic import Mark
from app.models.user import User
from app.schemas import MarkCreate, MarkResponse, MarkUpdate
from app.api.auth import get_current_user, get_db
from typing import List

router = APIRouter()


@router.post("/marks", response_model=MarkResponse)
def create_mark(
    mark: MarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    db_mark = Mark(**mark.model_dump())
    db.add(db_mark)
    db.commit()
    db.refresh(db_mark)
    return db_mark


@router.post("/marks/bulk")
def create_bulk_marks(
    marks: List[MarkCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    for mark in marks:
        existing = (
            db.query(Mark)
            .filter(
                Mark.student_id == mark.student_id,
                Mark.subject_id == mark.subject_id,
                Mark.exam_id == mark.exam_id,
            )
            .first()
        )
        if existing:
            existing.marks = mark.marks
        else:
            db.add(Mark(**mark.model_dump()))
    db.commit()
    return {"message": "Marks saved successfully"}


@router.get("/marks", response_model=List[MarkResponse])
def get_marks(
    exam_id: int = None,
    student_id: int = None,
    subject_id: int = None,
    db: Session = Depends(get_db),
):
    query = db.query(Mark)
    if exam_id:
        query = query.filter(Mark.exam_id == exam_id)
    if student_id:
        query = query.filter(Mark.student_id == student_id)
    if subject_id:
        query = query.filter(Mark.subject_id == subject_id)
    return query.all()


@router.put("/marks/{mark_id}", response_model=MarkResponse)
def update_mark(
    mark_id: int,
    mark: MarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    db_mark = db.query(Mark).filter(Mark.id == mark_id).first()
    if not db_mark:
        raise HTTPException(status_code=404, detail="Mark not found")
    for key, value in mark.model_dump(exclude_unset=True).items():
        setattr(db_mark, key, value)
    db.commit()
    db.refresh(db_mark)
    return db_mark


@router.get("/marks/student/{student_id}/exam/{exam_id}")
def get_student_exam_marks(
    student_id: int, exam_id: int, db: Session = Depends(get_db)
):
    marks = (
        db.query(Mark)
        .filter(Mark.student_id == student_id, Mark.exam_id == exam_id)
        .all()
    )
    return marks
