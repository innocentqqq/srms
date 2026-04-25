from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.auth import get_current_user, get_db
from app.models.user import User
from app.models.student import Student
from app.models.academic import Assignment, Submission, CourseSection, ActivityCompletion, Material
from app.schemas import SubmissionCreate, SubmissionResponse, CourseSectionResponse

router = APIRouter()

@router.post("/submissions", response_model=SubmissionResponse)
def submit_assignment(submission: SubmissionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")
        
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    existing = db.query(Submission).filter(
        Submission.assignment_id == submission.assignment_id,
        Submission.student_id == student.id
    ).first()
    
    if existing:
        existing.file_path = submission.file_path
        existing.submitted_at = __import__("datetime").datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    db_submission = Submission(
        assignment_id=submission.assignment_id,
        student_id=student.id,
        file_path=submission.file_path
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

@router.get("/my-submissions", response_model=List[SubmissionResponse])
def get_my_submissions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    return db.query(Submission).filter(Submission.student_id == student.id).all()

@router.post("/toggle-completion")
def toggle_completion(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can mark completion")
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    material_id = data.get("material_id")
    assignment_id = data.get("assignment_id")

    existing = db.query(ActivityCompletion).filter(
        ActivityCompletion.student_id == student.id,
        ActivityCompletion.material_id == material_id,
        ActivityCompletion.assignment_id == assignment_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"completed": False}
    
    new_comp = ActivityCompletion(
        student_id=student.id,
        material_id=material_id,
        assignment_id=assignment_id
    )
    db.add(new_comp)
    db.commit()
    return {"completed": True}

@router.get("/progress/{subject_id}")
def get_subject_progress(subject_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student: return {"percent": 0}

    materials = db.query(Material).filter(Material.subject_id == subject_id).all()
    assignments = db.query(Assignment).filter(Assignment.subject_id == subject_id).all()
    
    total_items = len(materials) + len(assignments)
    if total_items == 0: return {"percent": 100}

    completed_count = db.query(ActivityCompletion).filter(
        ActivityCompletion.student_id == student.id,
        (ActivityCompletion.material_id.in_([m.id for m in materials]) if materials else False) |
        (ActivityCompletion.assignment_id.in_([a.id for a in assignments]) if assignments else False)
    ).count()

    return {"percent": round((completed_count / total_items) * 100)}
