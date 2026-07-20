from pydantic import BaseModel

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = {}

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: dict | None = None
