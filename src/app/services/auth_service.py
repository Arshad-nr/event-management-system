from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Student
from app.schemas.student import StudentRegisterRequest, StudentLoginRequest
from app.core.security import hash_password, verify_password, create_access_token
from app.services.exceptions import DuplicateEmailException, InvalidCredentialsException

async def register_student(db: AsyncSession, data: StudentRegisterRequest) -> Student:
    result = await db.execute(select(Student).where(Student.email == data.email))
    if result.scalars().first():
        raise DuplicateEmailException()
    
    hashed_pw = hash_password(data.password)
    new_student = Student(
        name=data.name,
        email=data.email,
        password_hash=hashed_pw,
    )
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    return new_student

async def login_student(db: AsyncSession, data: StudentLoginRequest) -> str:
    result = await db.execute(select(Student).where(Student.email == data.email))
    student = result.scalars().first()
    
    if not student or not verify_password(data.password, student.password_hash):
        raise InvalidCredentialsException()
        
    access_token = create_access_token(data={"sub": str(student.id)})
    return access_token
