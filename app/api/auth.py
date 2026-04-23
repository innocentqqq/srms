from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import bcrypt
from datetime import datetime, timedelta, date
from jose import JWTError, jwt
from app.core.database import SessionLocal, Base, engine
from app.models.user import User, Teacher
from app.models.student import Student, Class
from app.models.academic import Subject, Exam, Mark
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
    ClassCreate,
    ClassResponse,
    SubjectCreate,
    SubjectResponse,
    ExamCreate,
    ExamResponse,
    MarkCreate,
    MarkResponse,
    MarkUpdate,
    ResultSummary,
)
from typing import List, Optional
import time

SECRET_KEY = "srms_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(status_code=401, detail="Invalid credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    if user.role == "teacher":
        teacher = Teacher(user_id=db_user.id, teacher_id=f"T{db_user.id:04d}")
        db.add(teacher)
        db.commit()
    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    if db.query(User).first():
        return {"message": "Data already exists"}

    admin = User(
        email="admin@school.com",
        username="admin",
        hashed_password=hash_password("admin123"),
        full_name="School Admin",
        role="admin",
    )
    teacher = User(
        email="teacher@school.com",
        username="teacher",
        hashed_password=hash_password("teacher123"),
        full_name="John Teacher",
        role="teacher",
    )
    student_user = User(
        email="student@school.com",
        username="student",
        hashed_password=hash_password("student123"),
        full_name="Aung Aung",
        role="student",
    )
    db.add_all([admin, teacher, student_user])
    db.commit()
    db.refresh(admin)
    db.refresh(teacher)
    db.refresh(student_user)

    db_teacher = Teacher(user_id=teacher.id, teacher_id="T0001", phone="0912345678")
    db.add(db_teacher)

    db_student = Student(
        user_id=student_user.id,
        student_id="S0001",
        name="Aung Aung",
        dob=date(2010, 5, 15),
        class_id=1,
        parent_name="U Tun Aung",
        phone="0911111111",
        address="Yangon",
        created_at=int(time.time()),
    )
    db.add(db_student)

    classes = [Class(class_name=f"Grade {i}", year=2024) for i in range(6, 11)]
    db.add_all(classes)
    db.commit()

    subjects_data = [
        ("Math", 1),
        ("English", 1),
        ("Physics", 1),
        ("Chemistry", 1),
        ("Biology", 1),
        ("History", 1),
        ("Math", 2),
        ("English", 2),
        ("Physics", 2),
        ("Chemistry", 2),
        ("Biology", 2),
        ("History", 2),
        ("Math", 3),
        ("English", 3),
        ("Physics", 3),
        ("Chemistry", 3),
        ("Biology", 3),
        ("History", 3),
        ("Math", 4),
        ("English", 4),
        ("Physics", 4),
        ("Chemistry", 4),
        ("Biology", 4),
        ("History", 4),
        ("Math", 5),
        ("English", 5),
        ("Physics", 5),
        ("Chemistry", 5),
        ("Biology", 5),
        ("History", 5),
    ]
    for name, class_id in subjects_data:
        db.add(Subject(subject_name=name, class_id=class_id))
    db.commit()

    exam = Exam(
        exam_name="Midterm Exam",
        term="First",
        year=2024,
        class_id=1,
        exam_date=date(2024, 10, 15),
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    subjects = db.query(Subject).filter(Subject.class_id == 1).all()
    students = db.query(Student).all()
    for student in students:
        for subject in subjects[:3]:
            mark = Mark(
                student_id=student.id,
                subject_id=subject.id,
                exam_id=exam.id,
                marks=float(70 + (student.id * 5) % 30),
            )
            db.add(mark)
    db.commit()

    return {"message": "Seed data created successfully"}
