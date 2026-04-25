from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.auth import get_current_user, get_db
from app.models.user import User, Parent
from app.models.student import Student
from app.models.academic import Attendance, Mark, Submission, Assignment
from app.schemas import AttendanceResponse, MarkResponse, SubmissionResponse, StudentResponse

router = APIRouter()

@router.get("/my-children", response_model=List[StudentResponse])
def get_my_children(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can access this")
    
    parent = db.query(Parent).filter(Parent.user_id == current_user.id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent record not found")
    
    return parent.students

@router.get("/child/{student_id}/attendance", response_model=List[AttendanceResponse])
def get_child_attendance(student_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    parent = db.query(Parent).filter(Parent.user_id == current_user.id).first()
    # Security check: Ensure this student is indeed linked to this parent
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student or parent not in student.parents:
         raise HTTPException(status_code=403, detail="Access denied to this student's data")
    
    return db.query(Attendance).filter(Attendance.student_id == student_id).all()

@router.get("/child/{student_id}/marks", response_model=List[MarkResponse])
def get_child_marks(student_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    parent = db.query(Parent).filter(Parent.user_id == current_user.id).first()
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student or parent not in student.parents:
         raise HTTPException(status_code=403, detail="Access denied")
    
    return db.query(Mark).filter(Mark.student_id == student_id).all()

@router.get("/child/{student_id}/submissions", response_model=List[SubmissionResponse])
def get_child_submissions(student_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    parent = db.query(Parent).filter(Parent.user_id == current_user.id).first()
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student or parent not in student.parents:
         raise HTTPException(status_code=403, detail="Access denied")
    
    return db.query(Submission).filter(Submission.student_id == student_id).all()
