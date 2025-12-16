from typing import List
from models.course import Course
from models.SearchCriteria import SearchCriteria
from patterns.search.search_strategy import SearchStrategy
from database.course_service import CourseService
from database.category_service import CategoryService

class CategorySearchStrategy(SearchStrategy):
    def __init__(self):
        self.course_service = CourseService()
        self.category_service = CategoryService()

    def search(self, criteria: SearchCriteria) -> List[Course]:
        # If no category specified, return all (or empty? Standard is ignore filter)
        # But if this strategy is CALLED, it implies we want to filter by category.
        # However, for standalone usage, let's assume if category is None, we return all.
        
        target_cat_id = None
        if criteria.category:
            cat = self.category_service.get_category_by_name(criteria.category)
            if cat:
                target_cat_id = cat["categoryId"]
            else:
                # Category specified but not found -> return empty
                return []
        else:
            # No category specified in criteria, return all (allow composite to handle intersection)
            all_courses = self.course_service.get_published_courses()
            return self._to_objects(all_courses)

        # We have a target_cat_id
        # Optimization: If CourseService had get_courses_by_category, we'd use it.
        # currently we filter manually.
        all_courses = self.course_service.get_published_courses()
        filtered = []
        for doc in all_courses:
            if doc.get("categoryId") == target_cat_id:
                filtered.append(doc)
        
        return self._to_objects(filtered)

    def _to_objects(self, course_docs) -> List[Course]:
        obj_list = []
        for doc in course_docs:
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
            obj_list.append(c)
        return obj_list
