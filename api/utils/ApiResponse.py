from typing import Generic, TypeVar, Optional
from abc import ABC, abstractmethod

T = TypeVar("T")

class MetaData:
    def __init__(self, total: int, page: int, limit: int):
        self.total = total
        self.page = page
        self.limit = limit

class ApiResponse(Generic[T], ABC):
    def __init__(
        self,
        status_code: int,
        message: str,
        data: Optional[T] = None,
        metadata: Optional[MetaData] = None
    ):
        self.status_code = status_code
        self.message = message
        self.data = data
        self.metadata = metadata

    @abstractmethod
    def _type(self) -> str:
        """Marker method to prevent direct instantiation"""

    @staticmethod
    def success(
        status_code: int,
        message: str,
        data: Optional[T] = None,
        metadata: Optional[MetaData] = None
    ) -> "ApiResponse[T]":
        return _SuccessResponse(status_code, message, data, metadata)

    @staticmethod
    def error(
        status_code: int,
        message: str,
        data: Optional[T] = None
    ) -> "ApiResponse[T]":
        return _ErrorResponse(status_code, message, data)


class _SuccessResponse(ApiResponse[T]):
    def _type(self) -> str:
        return "success"

class _ErrorResponse(ApiResponse[T]):
    def _type(self) -> str:
        return "error"