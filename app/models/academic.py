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
    sections = relationship("CourseSection", back_populates="subject")
    assignments = relationship("Assignment", back_populates="subject")
    grade_categories = relationship("GradeCategory", back_populates="subject")


class SubjectAssignment(Base):
    __tablename__ = "subject_assignments"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))

    subject = relationship("Subject", back_populates="teacher_assignments")
    teacher = relationship("Teacher", back_populates="subject_assignments")


class CourseSection(Base):
    __tablename__ = "course_sections"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)

    subject = relationship("Subject", back_populates="sections")
    materials = relationship("Material", back_populates="section")
    assignments = relationship("Assignment", back_populates="section")


class GradeCategory(Base):
    __tablename__ = "grade_categories"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    name = Column(String)  # e.g., "Homework", "Final Exam"
    weight = Column(Float)  # e.g., 0.2 for 20%

    subject = relationship("Subject", back_populates="grade_categories")
    assignments = relationship("Assignment", back_populates="category")
    exams = relationship("Exam", back_populates="category")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    section_id = Column(Integer, ForeignKey("course_sections.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("grade_categories.id"), nullable=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime)
    max_score = Column(Float, default=100.0)

    subject = relationship("Subject", back_populates="assignments")
    section = relationship("CourseSection", back_populates="assignments")
    category = relationship("GradeCategory", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    file_path = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    grade = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String)
    term = Column(String)
    year = Column(Integer)
    class_id = Column(Integer, ForeignKey("classes.id"))
    exam_date = Column(Date)
    category_id = Column(Integer, ForeignKey("grade_categories.id"), nullable=True)

    marks = relationship("Mark", back_populates="exam")
    category = relationship("GradeCategory", back_populates="exams")


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
    section_id = Column(Integer, ForeignKey("course_sections.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Subject", back_populates="materials")
    section = relationship("CourseSection", back_populates="materials")
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


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # CREATE, UPDATE, DELETE
    table_name = Column(String)
    record_id = Column(Integer)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    event_type = Column(String)  # holiday, assembly, event
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)  # Null = School-wide
    author_id = Column(Integer, ForeignKey("users.id"))

    class_obj = relationship("Class")
    author = relationship("User")


class ActivityCompletion(Base):
    __tablename__ = "activity_completions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student")
    material = relationship("Material")
    assignment = relationship("Assignment")


class BehaviorRecord(Base):
    __tablename__ = "behavior_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    type = Column(String)  # Merit, Demerit
    points = Column(Integer, default=0)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student")
    teacher = relationship("Teacher")
