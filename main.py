from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models import user, student, academic
from app.api import auth, students, classes, subjects, exams, marks, results, teacher

user.Base.metadata.create_all(bind=engine)
student.Base.metadata.create_all(bind=engine)
academic.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatic Seeding
    db: Session = SessionLocal()
    try:
        if not db.query(user.User).filter(user.User.role == "admin").first():
            print("Auto-seeding initial admin and classes...")
            admin = user.User(
                email="admin@school.com",
                username="admin",
                hashed_password=auth.hash_password("admin123"),
                full_name="School Admin",
                role="admin",
            )
            db.add(admin)
            classes_list = [
                student.Class(class_name=f"Grade {i}", year=2024) for i in range(6, 11)
            ]
            db.add_all(classes_list)
            db.commit()
            print("Auto-seeding complete.")
    finally:
        db.close()
    yield


app = FastAPI(title="School Result Management System", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(students.router, prefix="/api", tags=["Students"])
app.include_router(classes.router, prefix="/api", tags=["Classes"])
app.include_router(subjects.router, prefix="/api", tags=["Subjects"])
app.include_router(exams.router, prefix="/api", tags=["Exams"])
app.include_router(marks.router, prefix="/api", tags=["Marks"])
app.include_router(results.router, prefix="/api", tags=["Results"])
app.include_router(teacher.router, prefix="/api/teacher", tags=["Teacher"])

from app.api import pages

app.include_router(pages.router)
