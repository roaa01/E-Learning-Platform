from abc import ABC, abstractmethod
from typing import List, Any
from models.course import Course
from models.SearchCriteria import SearchCriteria

class SearchStrategy(ABC):
    @abstractmethod
    def search(self, criteria: SearchCriteria) -> List[Course]:
        """
        Execute search based on the provided criteria.
        
        Args:
            criteria (SearchCriteria): The search criteria containing query, filters, etc.
            
        Returns:
            List[Course]: A list of courses matching the criteria.
        """
        pass
