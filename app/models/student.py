from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base
import time

# Association table for many-to-many relationship between students and parents
student_parents = Table(
    "student_parents",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("parent_id", Integer, ForeignKey("parents.id"), primary_key=True),
)


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    student_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    dob = Column(Date)
    class_id = Column(Integer, ForeignKey("classes.id"))
    parent_name = Column(String)
    phone = Column(String)
    address = Column(String, nullable=True)
    created_at = Column(Integer, nullable=True)

    user = relationship("User", back_populates="student")
    class_obj = relationship("Class", back_populates="students")
    marks = relationship("Mark", back_populates="student")
    parents = relationship("Parent", secondary=student_parents, back_populates="students")
    submissions = relationship("Submission", back_populates="student")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String)
    year = Column(Integer)

    students = relationship("Student", back_populates="class_obj")
    subjects = relationship("Subject", back_populates="class_obj")
