from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class MetaData(BaseModel):
    total: int
    page: int
    limit: int

class ApiResponse(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: Optional[T] = None
    metadata: Optional[MetaData] = None

    @staticmethod
    def success(
        status_code: int,
        message: str,
        data: Optional[Any] = None,
        metadata: Optional[MetaData] = None
    ) -> "ApiResponse":
        return ApiResponse(
            status_code=status_code,
            message=message,
            data=data,
            metadata=metadata
        )

    @staticmethod
    def error(
        status_code: int,
        message: str,
        data: Optional[Any] = None
    ) -> "ApiResponse":
        return ApiResponse(
            status_code=status_code,
            message=message,
            data=data
        )