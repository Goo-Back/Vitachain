"""Pagination utilities for API responses."""

from typing import Dict, Any, Optional, List, TypeVar, Generic
from pydantic import BaseModel, Field
import math

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters."""
    limit: int = Field(default=50, ge=1, le=1000, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    
    @property
    def page(self) -> int:
        """Calculate page number from offset."""
        return math.floor(self.offset / self.limit) + 1 if self.limit > 0 else 1


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    limit: int = Field(description="Items per page")
    offset: int = Field(description="Items skipped")
    page: int = Field(description="Current page number")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether next page exists")
    has_previous: bool = Field(description="Whether previous page exists")
    
    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams) -> "PaginatedResponse[T]":
        """Create paginated response from items and parameters."""
        total_pages = math.ceil(total / params.limit) if params.limit > 0 else 1
        has_next = params.offset + params.limit < total
        has_previous = params.offset > 0
        
        return cls(
            items=items,
            total=total,
            limit=params.limit,
            offset=params.offset,
            page=params.page,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )


def paginate_query(query: str, params: PaginationParams) -> Dict[str, Any]:
    """Generate paginated SQL query components."""
    return {
        "select_clause": query,
        "limit_clause": f"LIMIT {params.limit}",
        "offset_clause": f"OFFSET {params.offset}",
        "full_query": f"{query} LIMIT {params.limit} OFFSET {params.offset}"
    }


def get_pagination_params(limit: Optional[int] = None, offset: Optional[int] = None) -> PaginationParams:
    """Get pagination parameters from request args."""
    return PaginationParams(
        limit=limit or 50,
        offset=offset or 0
    )
