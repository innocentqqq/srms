from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from app.api.auth import get_current_user, get_db
from app.models.user import User, Teacher
from app.models.student import Student, Class
from app.models.academic import Subject, SubjectAssignment, Attendance, Announcement, Material, Timetable, CourseSection, Assignment, Submission, GradeCategory, BehaviorRecord
from app.schemas import (
    AttendanceCreate,
    AttendanceResponse,
    AnnouncementCreate,
    AnnouncementResponse,
    MaterialCreate,
    MaterialResponse,
    TimetableCreate,
    TimetableResponse,
    ClassResponse,
    SubjectResponse,
    TeacherResponse,
    CourseSectionCreate,
    CourseSectionResponse,
    AssignmentCreate,
    AssignmentResponse,
    SubmissionResponse,
    SubmissionGrade,
    GradeCategoryCreate,
    GradeCategoryResponse,
    BehaviorRecordCreate,
    BehaviorRecordResponse,
)

router = APIRouter()


@router.get("/teachers", response_model=List[TeacherResponse])
def get_teachers(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    teachers = db.query(Teacher).all()
    results = []
    for t in teachers:
        results.append(
            TeacherResponse(
                id=t.id,
                teacher_id=t.teacher_id,
                full_name=t.user.full_name if t.user else "Unknown",
                email=t.user.email if t.user else "Unknown",
                phone=t.phone,
            )
        )
    return results


@router.delete("/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    user = teacher.user
    db.delete(teacher)
    if user:
        db.delete(user)
    db.commit()
    return {"message": "Teacher and associated user account deleted"}


@router.get("/assigned-subjects", response_model=List[SubjectResponse])
def get_assigned_subjects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        return db.query(Subject).all()
    
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers or admins can access this")
    
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher record not found")
    
    assignments = db.query(SubjectAssignment).filter(SubjectAssignment.teacher_id == teacher.id).all()
    subject_ids = [a.subject_id for a in assignments]
    subjects = db.query(Subject).filter(Subject.id.in_(subject_ids)).all()
    return subjects


@router.get("/class-students/{class_id}", response_model=List[dict])
def get_class_students(class_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    students = db.query(Student).filter(Student.class_id == class_id).all()
    return [{"id": s.id, "name": s.name, "student_id": s.student_id} for s in students]


@router.post("/attendance", response_model=List[AttendanceResponse])
def mark_attendance(attendance_list: List[AttendanceCreate], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can mark attendance")
    
    db_attendance = []
    for att in attendance_list:
        existing = db.query(Attendance).filter(
            Attendance.student_id == att.student_id,
            Attendance.date == att.date
        ).first()
        
        if existing:
            existing.status = att.status
            existing.remarks = att.remarks
            db_attendance.append(existing)
        else:
            new_att = Attendance(**att.dict())
            db.add(new_att)
            db_attendance.append(new_att)
            
    db.commit()
    for att in db_attendance:
        db.refresh(att)
    return db_attendance


@router.get("/attendance/{class_id}", response_model=List[AttendanceResponse])
def get_attendance(class_id: int, date: Optional[date] = None, db: Session = Depends(get_db)):
    query = db.query(Attendance).filter(Attendance.class_id == class_id)
    if date:
        query = query.filter(Attendance.date == date)
    return query.all()


@router.get("/attendance/stats/{student_id}")
def get_student_attendance_stats(student_id: int, db: Session = Depends(get_db)):
    total = db.query(Attendance).filter(Attendance.student_id == student_id).count()
    if total == 0: return {"percent": 100}
    present = db.query(Attendance).filter(Attendance.student_id == student_id, Attendance.status == "Present").count()
    return {"percent": round((present / total) * 100)}


@router.post("/announcements", response_model=AnnouncementResponse)
def create_announcement(announcement: AnnouncementCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    db_announcement = Announcement(
        **announcement.dict(),
        author_id=current_user.id
    )
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement


@router.get("/announcements", response_model=List[AnnouncementResponse])
def get_announcements(class_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Announcement)
    if class_id:
        query = query.filter((Announcement.class_id == class_id) | (Announcement.class_id == None))
    else:
        query = query.filter(Announcement.class_id == None)
    return query.order_by(Announcement.created_at.desc()).all()


@router.post("/materials", response_model=MaterialResponse)
def create_material(material: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can upload materials")
    
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher record not found")
        
    db_material = Material(
        title=material.get("title"),
        description=material.get("description"),
        subject_id=material.get("subject_id"),
        deadline=datetime.fromisoformat(material.get("deadline")) if material.get("deadline") else None,
        teacher_id=teacher.id
    )
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


@router.get("/materials/{subject_id}", response_model=List[MaterialResponse])
def get_materials(subject_id: int, section_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Material).filter(Material.subject_id == subject_id)
    if section_id:
        query = query.filter(Material.section_id == section_id)
    return query.all()


@router.get("/timetable", response_model=List[TimetableResponse])
def get_teacher_timetable(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view their timetable")
    
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    assignments = db.query(SubjectAssignment).filter(SubjectAssignment.teacher_id == teacher.id).all()
    subject_ids = [a.subject_id for a in assignments]
    
    return db.query(Timetable).filter(Timetable.subject_id.in_(subject_ids)).all()


@router.get("/timetable/class/{class_id}", response_model=List[TimetableResponse])
def get_class_timetable(class_id: int, db: Session = Depends(get_db)):
    return db.query(Timetable).filter(Timetable.class_id == class_id).all()


@router.post("/timetable", response_model=TimetableResponse)
def create_timetable(timetable: TimetableCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    db_timetable = Timetable(**timetable.dict())
    db.add(db_timetable)
    db.commit()
    db.refresh(db_timetable)
    return db_timetable


@router.delete("/timetable/{timetable_id}")
def delete_timetable(timetable_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    db_t = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not db_t:
        raise HTTPException(status_code=404, detail="Not found")
    
    db.delete(db_t)
    db.commit()
    return {"message": "Deleted"}


@router.post("/sections", response_model=CourseSectionResponse)
def create_section(section: CourseSectionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    db_section = CourseSection(**section.model_dump())
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section


@router.get("/sections/{subject_id}", response_model=List[CourseSectionResponse])
def get_sections(subject_id: int, db: Session = Depends(get_db)):
    return db.query(CourseSection).filter(CourseSection.subject_id == subject_id).order_by(CourseSection.order).all()


@router.post("/grade-categories", response_model=GradeCategoryResponse)
def create_grade_category(category: GradeCategoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    db_cat = GradeCategory(**category.model_dump())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@router.get("/grade-categories/{subject_id}", response_model=List[GradeCategoryResponse])
def get_grade_categories(subject_id: int, db: Session = Depends(get_db)):
    return db.query(GradeCategory).filter(GradeCategory.subject_id == subject_id).all()


@router.post("/assignments", response_model=AssignmentResponse)
def create_assignment(assignment: AssignmentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    db_assignment = Assignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


@router.get("/assignments/{subject_id}", response_model=List[AssignmentResponse])
def get_assignments(subject_id: int, section_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Assignment).filter(Assignment.subject_id == subject_id)
    if section_id:
        query = query.filter(Assignment.section_id == section_id)
    return query.all()


@router.get("/submissions/{assignment_id}", response_model=List[SubmissionResponse])
def get_submissions(assignment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return db.query(Submission).filter(Submission.assignment_id == assignment_id).all()


@router.put("/submissions/{submission_id}", response_model=SubmissionResponse)
def grade_submission(submission_id: int, grade_data: SubmissionGrade, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    db_submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    db_submission.grade = grade_data.grade
    db_submission.feedback = grade_data.feedback
    db.commit()
    db.refresh(db_submission)
    return db_submission


@router.post("/behavior", response_model=BehaviorRecordResponse)
def create_behavior_record(record: BehaviorRecordCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    db_record = BehaviorRecord(
        **record.model_dump(),
        teacher_id=teacher.id if teacher else None
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/behavior/{student_id}", response_model=List[BehaviorRecordResponse])
def get_student_behavior(student_id: int, db: Session = Depends(get_db)):
    return db.query(BehaviorRecord).filter(BehaviorRecord.student_id == student_id).all()
