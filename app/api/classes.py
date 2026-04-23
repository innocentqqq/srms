from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.student import Class
from app.models.user import User
from app.schemas import ClassCreate, ClassResponse
from app.api.auth import get_current_user, get_db
from typing import List

router = APIRouter()


@router.post("/classes", response_model=ClassResponse)
def create_class(
    class_obj: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_class = Class(**class_obj.model_dump())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class


@router.get("/classes", response_model=List[ClassResponse])
def get_classes(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.query(Class).all()


@router.get("/classes/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, db: Session = Depends(get_db)):
    db_class = db.query(Class).filter(Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class


@router.delete("/classes/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_class = db.query(Class).filter(Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(db_class)
    db.commit()
    return {"message": "Class deleted"}
