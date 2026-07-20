from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.student import StudentRegisterRequest, StudentLoginRequest, StudentResponse, TokenResponse
from app.schemas.common import SuccessResponse
from app.services import auth_service

router = APIRouter(prefix="/students", tags=["Authentication"])


@router.post("/register", response_model=SuccessResponse)
async def register(data: StudentRegisterRequest, db: AsyncSession = Depends(get_db)):
    student = await auth_service.register_student(db, data)
    student_resp = StudentResponse.model_validate(student, from_attributes=True)
    return SuccessResponse(
        message="Student registered successfully",
        data=student_resp.model_dump(mode="json"),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: StudentLoginRequest, db: AsyncSession = Depends(get_db)):
    token = await auth_service.login_student(db, data)
    return TokenResponse(access_token=token, token_type="bearer")
