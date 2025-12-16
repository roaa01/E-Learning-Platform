from typing import List
import random
from models.course import Course
from models.SearchCriteria import SearchCriteria
from patterns.search.search_strategy import SearchStrategy
from database.course_service import CourseService

class RecommendationSearchStrategy(SearchStrategy):
    def __init__(self):
        self.course_service = CourseService()

    def search(self, criteria: SearchCriteria) -> List[Course]:
        # For simplicity, we'll fetch all published courses and return a random sample
        # In a real app, this would use user preferences, viewing history, etc.
        
        published_courses = self.course_service.get_published_courses()
        
        # Convert to objects
        course_objects = []
        for doc in published_courses:
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
                modules=[]
            )
            course_objects.append(c)
        
        # Shuffle for "random" recommendation
        random.shuffle(course_objects)
        
        # Pagination
        start = (criteria.page - 1) * criteria.page_size
        end = start + criteria.page_size
        return course_objects[start:end]
