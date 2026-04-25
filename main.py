from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import engine, SessionLocal, Base
from app.models import user, student, academic
from app.api import auth, students, classes, subjects, exams, marks, results, teacher, lms

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
            
            # Check if classes already exist to avoid duplicates
            if not db.query(student.Class).first():
                classes_list = [
                    student.Class(class_name=f"Grade {i}", year=2024) for i in range(6, 11)
                ]
                db.add_all(classes_list)
                
            try:
                db.commit()
                print("Auto-seeding complete.")
            except IntegrityError:
                db.rollback()
                print("Auto-seeding skipped: already seeded.")
            except Exception as e:
                db.rollback()
                print(f"Auto-seeding failed: {e}")
    except Exception as e:
        print(f"Lifespan seeding error: {e}")
    finally:
        db.close()
    yield


app = FastAPI(title="School Result Management System", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok"}

app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(students.router, prefix="/api", tags=["Students"])
app.include_router(classes.router, prefix="/api", tags=["Classes"])
app.include_router(subjects.router, prefix="/api", tags=["Subjects"])
app.include_router(exams.router, prefix="/api", tags=["Exams"])
app.include_router(marks.router, prefix="/api", tags=["Marks"])
app.include_router(results.router, prefix="/api", tags=["Results"])
app.include_router(teacher.router, prefix="/api/teacher", tags=["Teacher"])
app.include_router(lms.router, prefix="/api/lms", tags=["LMS"])

from app.api import pages

app.include_router(pages.router)
