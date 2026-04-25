from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.student import Student, Class
from app.models.academic import Exam, Mark, Subject
from app.api.auth import get_current_user, get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@router.get("/admin/students", response_class=HTMLResponse)
def admin_students(request: Request):
    return templates.TemplateResponse(request, "students.html")


@router.get("/admin/teachers", response_class=HTMLResponse)
def admin_teachers(request: Request):
    return templates.TemplateResponse(request, "teachers.html")


@router.get("/admin/classes", response_class=HTMLResponse)
def admin_classes(request: Request):
    return templates.TemplateResponse(request, "classes.html")


@router.get("/admin/subjects", response_class=HTMLResponse)
def admin_subjects(request: Request):
    return templates.TemplateResponse(request, "subjects.html")


@router.get("/admin/exams", response_class=HTMLResponse)
def admin_exams(request: Request):
    return templates.TemplateResponse(request, "exams.html")


@router.get("/admin/teacher/{teacher_id}", response_class=HTMLResponse)
def admin_teacher_detail(request: Request, teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return templates.TemplateResponse(request, "teacher_detail.html", {"teacher": teacher})


@router.get("/admin/student/{student_id}", response_class=HTMLResponse)
def admin_student_detail(request: Request, student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse(request, "student_detail.html", {"student": student})


@router.get("/teacher/marks", response_class=HTMLResponse)
def teacher_marks(request: Request):
    return templates.TemplateResponse(request, "marks.html")


@router.get("/teacher/attendance", response_class=HTMLResponse)
def teacher_attendance(request: Request):
    return templates.TemplateResponse(request, "attendance.html")


@router.get("/teacher/materials", response_class=HTMLResponse)
def teacher_materials(request: Request):
    return templates.TemplateResponse(request, "materials.html")


@router.get("/teacher/timetable", response_class=HTMLResponse)
def teacher_timetable(request: Request):
    return templates.TemplateResponse(request, "timetable.html")


@router.get("/course/{subject_id}", response_class=HTMLResponse)
def course_detail(request: Request, subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return templates.TemplateResponse(request, "course_detail.html", {"subject": subject})


@router.get("/results", response_class=HTMLResponse)
def results_page(request: Request):
    return templates.TemplateResponse(request, "results.html")


@router.get("/report-card/{student_id}/{exam_id}", response_class=HTMLResponse)
def report_card(
    request: Request, student_id: int, exam_id: int, db: Session = Depends(get_db)
):
    from app.api.results import calculate_gpa

    student = db.query(Student).filter(Student.id == student_id).first()
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    marks = (
        db.query(Mark)
        .filter(Mark.student_id == student_id, Mark.exam_id == exam_id)
        .all()
    )
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
                "subject_name": subject.subject_name if subject else "Unknown",
                "marks": m.marks,
            }
        )

    return templates.TemplateResponse(
        request,
        "report_card.html",
        {
            "student": student,
            "exam": exam,
            "class_obj": class_obj,
            "subjects": subjects_data,
            "total": round(total, 2),
            "average": round(avg, 2),
            "gpa": gpa,
        },
    )
