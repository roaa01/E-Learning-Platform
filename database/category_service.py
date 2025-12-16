from typing import Optional, Dict, Any, List
from .seed import get_database
from models.category import Category
from models.course import Course

class CategoryService:
    def __init__(self):
        self.db = get_database()
        self.categories = self.db.get_collection("categories")

    def create_category(self, category_id: int, name: str, description: str) -> bool:
        category_doc = {
            "categoryId": category_id,
            "name": name,
            "description": description,
            "courses": []
        }
        try:
            self.categories.insert_one(category_doc)
            return True
        except Exception as e:
            print(f"Error creating category: {e}")
            return False

    def get_category(self, category_id: int) -> Optional[Dict[str, Any]]:
        return self.categories.find_one({"categoryId": category_id})

    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return self.categories.find_one({"name": name})

    def get_all_categories(self) -> List[Dict[str, Any]]:
        return list(self.categories.find({}))

    def add_course_to_category(self, category_id: int, course_id: str) -> bool:
        res = self.categories.update_one(
            {"categoryId": category_id},
            {"$addToSet": {"courses": course_id}}
        )
        return res.modified_count > 0

    def remove_course_from_category(self, category_id: int, course_id: str) -> bool:
        res = self.categories.update_one(
            {"categoryId": category_id},
            {"$pull": {"courses": course_id}}
        )
        return res.modified_count > 0

    def get_category_with_courses(self, category_id: int) -> Optional[Category]:
        cat_data = self.categories.find_one({"categoryId": category_id})
        if not cat_data:
            return None
        
        # Get course IDs
        course_ids = cat_data.get("courses", [])
        
        # Fetch courses from DB
        courses_collection = self.db.get_collection("courses")
        course_docs = list(courses_collection.find({"id": {"$in": course_ids}}))
        
        # Convert to Course objects
        course_objects = []
        for doc in course_docs:
            # Map DB fields to Course model fields
            # Ensure we handle ObjectId vs str id if needed
            c = Course(
                id=doc.get("id"),
                title=doc.get("title", ""),
                description=doc.get("description", ""),
                instructorId=doc.get("instructorId"),
                # category=doc.get("category", ""), # Removed from model 
                categoryId=doc.get("categoryId", 0), # Added to model
                status=doc.get("status", "draft"),
                createdDate=doc.get("createdDate"),
                # We can load modules if needed, or keep empty list if shallow load desired. 
                # Request implies "list of courses", usually summaries, but let's load what we can easily.
                # Transforming modules might be complex if not serializing properly, keeping simple for now.
                modules=[] 
            )
            course_objects.append(c)
            
        return Category(
            categoryId=cat_data["categoryId"],
            name=cat_data["name"],
            description=cat_data["description"],
            courses=course_objects
        )
