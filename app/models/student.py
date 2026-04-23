from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import time


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


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String)
    year = Column(Integer)

    students = relationship("Student", back_populates="class_obj")
    subjects = relationship("Subject", back_populates="class_obj")
