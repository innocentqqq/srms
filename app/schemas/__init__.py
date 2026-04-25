from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


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
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    class_id: Optional[int] = None

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


class StudentAccountCreate(StudentCreate):
    password: str
    username: str
    email: str


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


class TeacherBase(BaseModel):
    teacher_id: str
    full_name: str
    email: str
    phone: Optional[str] = None


class TeacherCreate(TeacherBase):
    pass


class TeacherAccountCreate(TeacherCreate):
    password: str
    username: str


class TeacherResponse(TeacherBase):
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


class CourseSectionBase(BaseModel):
    subject_id: int
    title: str
    description: Optional[str] = None
    order: int = 0


class CourseSectionCreate(CourseSectionBase):
    pass


class CourseSectionResponse(CourseSectionBase):
    id: int

    class Config:
        from_attributes = True


class GradeCategoryBase(BaseModel):
    subject_id: int
    name: str
    weight: float


class GradeCategoryCreate(GradeCategoryBase):
    pass


class GradeCategoryResponse(GradeCategoryBase):
    id: int

    class Config:
        from_attributes = True


class AssignmentBase(BaseModel):
    subject_id: int
    section_id: Optional[int] = None
    category_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    due_date: datetime
    max_score: float = 100.0


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentResponse(AssignmentBase):
    id: int

    class Config:
        from_attributes = True


class SubmissionBase(BaseModel):
    assignment_id: int
    student_id: int


class SubmissionCreate(SubmissionBase):
    file_path: Optional[str] = None


class SubmissionGrade(BaseModel):
    grade: float
    feedback: Optional[str] = None


class SubmissionResponse(SubmissionBase):
    id: int
    file_path: Optional[str] = None
    submitted_at: datetime
    grade: Optional[float] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    table_name: str
    record_id: int
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    event_type: str
    class_id: Optional[int] = None


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventResponse(CalendarEventBase):
    id: int
    author_id: int

    class Config:
        from_attributes = True
