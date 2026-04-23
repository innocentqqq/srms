from pydantic import BaseModel
from typing import Optional
from datetime import date


class UserBase(BaseModel):
    email: str
    username: str
    full_name: str


class UserCreate(UserBase):
    password: str
    role: str = "student"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class StudentBase(BaseModel):
    student_id: str
    name: str
    dob: date
    class_id: int
    parent_name: str
    phone: str
    address: Optional[str] = ""


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    class_id: Optional[int] = None
    parent_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True


class ClassBase(BaseModel):
    class_name: str
    year: int


class ClassCreate(ClassBase):
    pass


class ClassResponse(ClassBase):
    id: int

    class Config:
        from_attributes = True


class SubjectBase(BaseModel):
    subject_name: str
    class_id: int


class SubjectCreate(SubjectBase):
    pass


class SubjectResponse(SubjectBase):
    id: int

    class Config:
        from_attributes = True


class ExamBase(BaseModel):
    exam_name: str
    term: str
    year: int
    class_id: int
    exam_date: date


class ExamCreate(ExamBase):
    pass


class ExamResponse(ExamBase):
    id: int

    class Config:
        from_attributes = True


class MarkBase(BaseModel):
    student_id: int
    subject_id: int
    exam_id: int
    marks: float


class MarkCreate(MarkBase):
    pass


class MarkUpdate(BaseModel):
    marks: Optional[float] = None


class MarkResponse(MarkBase):
    id: int

    class Config:
        from_attributes = True


class ResultSummary(BaseModel):
    student_id: int
    student_name: str
    student_number: str
    class_name: str
    exam_name: str
    total_marks: float
    average: float
    gpa: float
    rank: int
    subjects: list


from datetime import datetime


class AttendanceBase(BaseModel):
    student_id: int
    class_id: int
    date: date
    status: str
    remarks: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    id: int

    class Config:
        from_attributes = True


class AnnouncementBase(BaseModel):
    title: str
    content: str
    class_id: Optional[int] = None


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementResponse(AnnouncementBase):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject_id: int
    deadline: Optional[datetime] = None


class MaterialCreate(MaterialBase):
    teacher_id: int


class MaterialResponse(MaterialBase):
    id: int
    teacher_id: int
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TimetableBase(BaseModel):
    class_id: int
    subject_id: int
    day_of_week: str
    start_time: str
    end_time: str
    room: Optional[str] = None


class TimetableCreate(TimetableBase):
    pass


class TimetableResponse(TimetableBase):
    id: int

    class Config:
        from_attributes = True
