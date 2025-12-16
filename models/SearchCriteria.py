from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchCriteria:
    query: Optional[str] = None
    category: Optional[str] = None # category name or ID
    filter_type: Optional[str] = None # e.g. "by_title", "by_category"
    
    # New filters
    level: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    instructor_id: Optional[str] = None
    
    # Sorting / Strategy
    sort_by: Optional[str] = "recommended"
    
    # Pagination
    page: int = 1
    page_size: int = 10
