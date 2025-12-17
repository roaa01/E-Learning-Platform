from typing import List
from models.course import Course
from models.SearchCriteria import SearchCriteria
from .search_strategy import SearchStrategy

class SearchContext:
    def __init__(self, strategy: SearchStrategy = None):
        self._strategy = strategy

    def set_strategy(self, strategy: SearchStrategy):
        """Set the active search strategy"""
        self._strategy = strategy

    def execute_search(self, criteria: SearchCriteria) -> List[Course]:
        """Execute the search using the current strategy"""
        if not self._strategy:
            return []
        return self._strategy.search(criteria)
