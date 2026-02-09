"""
Common Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    """Standard response status values"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel):
    """Paginated API response"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = "Operation completed successfully"
    data: List[Any] = []
    pagination: PaginationMeta
    metadata: Optional[Dict[str, Any]] = None


class SortField(BaseModel):
    """Field sorting specification"""
    field: str
    direction: str = Field("asc", regex="^(asc|desc)$")


class FilterField(BaseModel):
    """Field filtering specification"""
    field: str
    value: Any
    operator: str = Field("eq", regex="^(eq|ne|gt|lt|gte|lte|in|not_in|contains)$")


class SearchParams(BaseModel):
    """Search and filter parameters"""
    query: Optional[str] = None
    filters: Optional[List[FilterField]] = []
    sort: Optional[List[SortField]] = []
    pagination: PaginationParams = PaginationParams()


class HealthStatus(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    environment: str
    database: bool
    services: Dict[str, bool]


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime
    updated_at: Optional[datetime] = None


class ErrorDetail(BaseModel):
    """Error detail information"""
    code: str
    message: str
    field: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ValidationError(BaseModel):
    """Validation error response"""
    status: ResponseStatus = ResponseStatus.ERROR
    message: str = "Validation failed"
    errors: List[ErrorDetail]