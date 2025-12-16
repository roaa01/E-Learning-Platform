from typing import List
from models.course import Course
from models.SearchCriteria import SearchCriteria
from patterns.search.search_strategy import SearchStrategy
from database.course_service import CourseService

class TitleSearchStrategy(SearchStrategy):
    def __init__(self):
        self.course_service = CourseService()

    def search(self, criteria: SearchCriteria) -> List[Course]:
        # Implementation relying on fetching all and filtering in-memory
        # (For production, this should be a DB query, but sticking to pattern structure)
        # Or ideally, we should expose a search method in service that accepts criteria.
        # Here we will implement the logic.
        
        all_courses_dicts = self.course_service.get_all_courses()
        
        # Filter by title
        query = criteria.query.lower() if criteria.query else ""
        filtered = []
        
        for doc in all_courses_dicts:
            title = doc.get("title", "").lower()
            if query in title:
                # Convert dict to Course object
                c = Course(
                    id=doc.get("id"),
                    title=doc.get("title"),
                    description=doc.get("description"),
                    instructorId=doc.get("instructorId"),
                    categoryId=doc.get("categoryId", 0),
                    level=doc.get("level", "Beginner"),
                    price=doc.get("price", 0.0),
                    status=doc.get("status"),
                    createdDate=doc.get("createdDate"),
                    modules=[] # keeping modules empty for list view performance
                )
                filtered.append(c)
                
        # Pagination
        start = (criteria.page - 1) * criteria.page_size
        end = start + criteria.page_size
        return filtered[start:end]
