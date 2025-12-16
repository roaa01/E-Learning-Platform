from typing import List
from models.course import Course
from models.SearchCriteria import SearchCriteria
from patterns.search.search_strategy import SearchStrategy
from database.course_service import CourseService
from database.category_service import CategoryService

from patterns.search.category_search_strategy import CategorySearchStrategy

from database.authservice import AuthService
from database.seed import get_database

class FilterSearchStrategy(SearchStrategy):
    def __init__(self):
        self.course_service = CourseService()
        self.category_service = CategoryService()
        self.category_strategy = CategorySearchStrategy()
        db = get_database()
        self.auth_service = AuthService(db.get_collection("users"))
        self.instructor_cache = {}

    def search(self, criteria: SearchCriteria) -> List[Course]:
        # Refactoring: Delegate category search to CategorySearchStrategy if category is present
        initial_courses = []
        if criteria.category:
            # Use the specialized strategy
            # Note: This returns List[Course] objects
            cat_courses = self.category_strategy.search(criteria)
            # Convert back to dicts for the existing pipeline (keeping consistency with other filters)
            initial_courses = [c.to_dict() for c in cat_courses]
        else:
            # No category filter, start with all published
            initial_courses = self.course_service.get_published_courses()

        all_courses_dicts = initial_courses
        
        filtered = []
        
        # We don't need to resolve category ID here anymore as the strategy handled it or we iterate result
        
        for doc in all_courses_dicts:
            # 1. Full-text search (Title & Description & *Instructor Name*)
            if criteria.query:
                q = criteria.query.lower()
                title = doc.get("title", "").lower()
                desc = doc.get("description", "").lower()
                
                # Resolve Instructor Name
                i_id = doc.get("instructorId")
                i_name = ""
                if i_id:
                    if i_id in self.instructor_cache:
                        i_name = self.instructor_cache[i_id]
                    else:
                        try:
                            u = self.auth_service.get_user_by_id(i_id)
                            if u:
                                name_val = u.name or u.full_name or u.email or ""
                                i_name = name_val.lower()
                                self.instructor_cache[i_id] = i_name
                        except:
                            pass
                
                # Check match
                if q not in title and q not in desc and q not in i_name:
                    continue

            # 2. Category match - Handled by initial fetch/strategy, but double check if needed?
            # If we trusted the strategy, we don't need to check again.
            
            # 3. Level match
            if criteria.level:
                if doc.get("level", "Beginner").lower() != criteria.level.lower():
                    continue

            # 4. Price match
            price = doc.get("price", 0.0)
            if criteria.min_price is not None and price < criteria.min_price:
                continue
            if criteria.max_price is not None and price > criteria.max_price:
                continue

            # 5. Instructor match
            if criteria.instructor_id:
                # Ensure string comparison
                i_id = str(doc.get("instructorId", ""))
                c_id = str(criteria.instructor_id)
                if i_id != c_id:
                    continue

            # Convert to Course object
            c = Course(
                id=doc.get("id"),
                title=doc.get("title"),
                description=doc.get("description"),
                instructor_id=doc.get("instructorId"),
                category_id=doc.get("categoryId", 0),
                level=doc.get("level", "Beginner"),
                price=doc.get("price", 0.0),
                status=doc.get("status"),
                created_date=doc.get("createdDate"),
                modules=[]
            )
            filtered.append(c)

        # Sorting / Recommendation
        if criteria.sort_by == "recommended":
            import random
            random.shuffle(filtered)
        # Could add price_asc, price_desc here

        # Pagination
        start = (criteria.page - 1) * criteria.page_size
        end = start + criteria.page_size
        return filtered[start:end]
