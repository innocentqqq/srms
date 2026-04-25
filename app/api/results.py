from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.student import Student, Class
from app.models.academic import Exam, Mark, Subject, GradeCategory, Assignment, Submission
from app.models.user import User
from app.api.auth import get_current_user, get_db
from typing import List
import io
from datetime import date

router = APIRouter()


def calculate_weighted_subject_grade(student_id: int, subject_id: int, db: Session) -> dict:
    categories = db.query(GradeCategory).filter(GradeCategory.subject_id == subject_id).all()
    if not categories:
        return {"total_grade": 0, "gpa": 0, "breakdown": [], "details": "No categories defined"}
    
    total_weighted_grade = 0
    cat_details = []
    
    for cat in categories:
        # Get all assessments in this category
        assignments = db.query(Assignment).filter(Assignment.category_id == cat.id).all()
        exams = db.query(Exam).filter(Exam.category_id == cat.id).all()
        
        cat_scores = []
        
        # Collect assignment grades
        for assign in assignments:
            submission = db.query(Submission).filter(
                Submission.assignment_id == assign.id,
                Submission.student_id == student_id
            ).first()
            if submission and submission.grade is not None:
                cat_scores.append((submission.grade / assign.max_score) * 100)
                
        # Collect exam marks
        for exam in exams:
            mark = db.query(Mark).filter(
                Mark.exam_id == exam.id,
                Mark.student_id == student_id,
                Mark.subject_id == subject_id
            ).first()
            if mark:
                cat_scores.append(mark.marks) 
                
        if cat_scores:
            cat_avg = sum(cat_scores) / len(cat_scores)
            weighted_contribution = cat_avg * cat.weight
            total_weighted_grade += weighted_contribution
            cat_details.append({
                "category": cat.name,
                "weight": cat.weight,
                "average": round(cat_avg, 2),
                "contribution": round(weighted_contribution, 2)
            })
            
    return {
        "total_grade": round(total_weighted_grade, 2),
        "gpa": calculate_gpa(total_weighted_grade),
        "breakdown": cat_details
    }


@router.get("/results/weighted/{student_id}/{subject_id}")
def get_weighted_result(student_id: int, subject_id: int, db: Session = Depends(get_db)):
    return calculate_weighted_subject_grade(student_id, subject_id, db)


def calculate_gpa(marks: float) -> float:
    if marks >= 80:
        return 4.0
    elif marks >= 70:
        return 3.0
    elif marks >= 60:
        return 2.0
    elif marks >= 50:
        return 1.0
    return 0.0


@router.get("/results/exam/{exam_id}")
def get_exam_results(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    marks_query = db.query(Mark).filter(Mark.exam_id == exam_id).all()
    student_ids = list(set([m.student_id for m in marks_query]))

    results = []
    for student_id in student_ids:
        student = db.query(Student).filter(Student.id == student_id).first()
        class_obj = (
            db.query(Class).filter(Class.id == student.class_id).first()
            if student
            else None
        )
        student_marks = [m for m in marks_query if m.student_id == student_id]

        total = sum([m.marks for m in student_marks])
        avg = total / len(student_marks) if student_marks else 0
        gpa = calculate_gpa(avg)

        subjects_data = []
        for m in student_marks:
            subject = db.query(Subject).filter(Subject.id == m.subject_id).first()
            subjects_data.append(
                {
                    "subject_name": subject.subject_name if subject else "Unknown",
                    "marks": m.marks,
                }
            )

        results.append(
            {
                "student_id": student.id,
                "student_name": student.name,
                "student_number": student.student_id,
                "class_name": class_obj.class_name if class_obj else "Unknown",
                "exam_name": exam.exam_name,
                "total_marks": round(total, 2),
                "average": round(avg, 2),
                "gpa": gpa,
                "subjects": subjects_data,
            }
        )

    results.sort(key=lambda x: x["average"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1

    return results


@router.get("/results/student/{student_id}")
def get_student_results(student_id: int, db: Session = Depends(get_db)):
    marks = db.query(Mark).filter(Mark.student_id == student_id).all()
    student = db.query(Student).filter(Student.id == student_id).first()

    results = []
    exam_ids = list(set([m.exam_id for m in marks]))
    for exam_id in exam_ids:
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        exam_marks = [m for m in marks if m.exam_id == exam_id]
        total = sum([m.marks for m in exam_marks])
        avg = total / len(exam_marks) if exam_marks else 0
        gpa = calculate_gpa(avg)

        results.append(
            {
                "exam_id": exam_id,
                "exam_name": exam.exam_name if exam else "Unknown",
                "total_marks": round(total, 2),
                "average": round(avg, 2),
                "gpa": gpa,
            }
        )

    return {"student": student, "results": results}


@router.get("/results/student/{student_id}/exam/{exam_id}")
def get_student_exam_result(
    student_id: int, exam_id: int, db: Session = Depends(get_db)
):
    marks = (
        db.query(Mark)
        .filter(Mark.student_id == student_id, Mark.exam_id == exam_id)
        .all()
    )
    student = db.query(Student).filter(Student.id == student_id).first()
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    class_obj = (
        db.query(Class).filter(Class.id == student.class_id).first()
        if student
        else None
    )

    total = sum([m.marks for m in marks])
    avg = total / len(marks) if marks else 0
    gpa = calculate_gpa(avg)

    subjects_data = []
    for m in marks:
        subject = db.query(Subject).filter(Subject.id == m.subject_id).first()
        subjects_data.append(
            {
                "subject_id": subject.id,
                "subject_name": subject.subject_name if subject else "Unknown",
                "marks": m.marks,
            }
        )

    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "student_id": student.student_id,
            "class_name": class_obj.class_name if class_obj else "Unknown",
        },
        "exam": exam,
        "total_marks": round(total, 2),
        "average": round(avg, 2),
        "gpa": gpa,
        "subjects": subjects_data,
    }
