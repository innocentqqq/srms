from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String)
    class_id = Column(Integer, ForeignKey("classes.id"))

    class_obj = relationship("Class", back_populates="subjects")
    marks = relationship("Mark", back_populates="subject")
    teacher_assignments = relationship("SubjectAssignment", back_populates="subject")
    materials = relationship("Material", back_populates="subject")
    timetables = relationship("Timetable", back_populates="subject")


class SubjectAssignment(Base):
    __tablename__ = "subject_assignments"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))

    subject = relationship("Subject", back_populates="teacher_assignments")
    teacher = relationship("Teacher", back_populates="subject_assignments")


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String)
    term = Column(String)
    year = Column(Integer)
    class_id = Column(Integer, ForeignKey("classes.id"))
    exam_date = Column(Date)

    marks = relationship("Mark", back_populates="exam")


class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    marks = Column(Float)

    student = relationship("Student", back_populates="marks")
    subject = relationship("Subject", back_populates="marks")
    exam = relationship("Exam", back_populates="marks")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    date = Column(Date)
    status = Column(String)  # Present, Absent, Late, Excused
    remarks = Column(String, nullable=True)

    student = relationship("Student")
    class_obj = relationship("Class")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)  # Null means all classes
    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User")
    class_obj = relationship("Class")


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Subject", back_populates="materials")
    teacher = relationship("Teacher")


class Timetable(Base):
    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    day_of_week = Column(String)  # Monday, Tuesday, etc.
    start_time = Column(String)  # e.g., "09:00"
    end_time = Column(String)  # e.g., "10:00"
    room = Column(String, nullable=True)

    class_obj = relationship("Class")
    subject = relationship("Subject", back_populates="timetables")
