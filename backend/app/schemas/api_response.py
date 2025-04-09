from typing import Optional, Any
from fastapi.responses import JSONResponse
from typing import Generic, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")

class APIResponse(GenericModel, Generic[T]):
    httpStatus: int
    data: Optional[T] = None
    message: Optional[str] = None

def success_response(data: Any = None, message: str = "요청이 성공적으로 처리되었습니다.", status_code: int = 200):
    return APIResponse(
        httpStatus=status_code,
        data=data,
        message=message
    )

