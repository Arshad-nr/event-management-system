import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field

class StudentRegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)

class StudentLoginRequest(BaseModel):
    email: EmailStr
    password: str

class StudentResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class StudentRegistrationInfo(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
