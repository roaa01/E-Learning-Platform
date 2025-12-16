from typing import Optional, Dict, Any, List
from bson import ObjectId
from datetime import datetime
from .seed import get_database
from models.course import Course, Module, Lesson


class CourseService:
    def __init__(self):
        self.db = get_database()
        self.courses = self.db.get_collection("courses")

    def create_course(self, title: str, description: str, instructor_id: str, category_name: str = "", visibility: str = "draft") -> str:
        # Use UML attribute names: id, instructorId, createdDate, status
        from database.category_service import CategoryService
        cat_service = CategoryService()
        
        # logic to find or create category
        cat_id = 0
        if category_name:
            existing_cat = cat_service.get_category_by_name(category_name)
            if existing_cat:
                cat_id = existing_cat["categoryId"]
            else:
                # Generate new ID (simple random for now, or finding max + 1)
                # In production, use a counter or ObjectId. Here, using hash for simplicity/uniqueness in small scale or just random
                import random
                cat_id = random.randint(1000, 99999) 
                success = cat_service.create_category(cat_id, category_name, "")
                if not success:
                    # Fallback or error handling
                    print("Failed to auto-create category")
        
        new_id = str(ObjectId())
        course_doc = {
            "id": new_id,
            "title": title,
            "description": description,
            "instructorId": instructor_id,
            "categoryId": cat_id, # Link via ID
            "status": visibility,
            "createdDate": datetime.utcnow(),
            "modules": [],
        }
        res = self.courses.insert_one(course_doc)
        
        # Link course to category
        if cat_id != 0:
            cat_service.add_course_to_category(cat_id, new_id)
            
        return new_id

    def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        # Allow fetching by internal ObjectId or by string `id` field
        try:
            doc = self.courses.find_one({"_id": ObjectId(course_id)})
            if doc:
                return doc
        except Exception:
            pass
        return self.courses.find_one({"id": course_id})

    def delete_course(self, course_id: str) -> bool:
        # Try deleting by string `id` field first, then by MongoDB ObjectId
        try:
            res = self.courses.delete_one({"id": course_id})
            if res.deleted_count > 0:
                return True
        except Exception:
            pass

        try:
            res = self.courses.delete_one({"_id": ObjectId(course_id)})
            return res.deleted_count == 1
        except Exception:
            return False

    def update_course(self, course_id: str, updates: Dict[str, Any]) -> bool:
        if "modules" in updates:
            # ensure modules structure is serializable
            updates["modules"] = [m if isinstance(m, dict) else m.to_dict() for m in updates["modules"]]
            
        print(f"[DEBUG] Attempting update for course_id: {course_id}")
        
        matched = False
        
        # 1. Try to update by MongoDB _id (if course_id is a valid ObjectId)
        try:
            oid = ObjectId(course_id)
            res = self.courses.update_one({"_id": oid}, {"$set": updates})
            if res.matched_count > 0:
                print(f"[DEBUG] Matched by _id")
                matched = True
        except Exception:
            # Not a valid ObjectId format, ignore this step
            pass

        # 2. If not found by _id, try to update by custom 'id' field
        if not matched:
            # We don't try/except here because we expect this to work or be the final attempt
            res = self.courses.update_one({"id": course_id}, {"$set": updates})
            if res.matched_count > 0:
                print(f"[DEBUG] Matched by custom id")
                matched = True
            else:
                print(f"[DEBUG] No match found for id: {course_id}")

        return matched

    def add_module(self, course_id: str, module_title: str) -> str:
        module = {"id": str(ObjectId()), "title": module_title, "lessons": []}
        # Query by id field (string) first, fall back to _id
        res = self.courses.update_one({"id": course_id}, {"$push": {"modules": module}})
        if res.matched_count == 0:
            # Try by MongoDB ObjectId
            try:
                res = self.courses.update_one({"_id": ObjectId(course_id)}, {"$push": {"modules": module}})
            except Exception:
                return ""
        if res.modified_count > 0:
            return module["id"]
        return ""

    def add_lesson(self, course_id: str, module_id: str, title: str, content: str, lesson_type: str) -> str:
        lesson = {"id": str(ObjectId()), "title": title, "content": content, "type": lesson_type, "resources": []}
        # Query by id field (string) first
        res = self.courses.update_one({"id": course_id, "modules.id": module_id}, {"$push": {"modules.$.lessons": lesson}})
        if res.matched_count == 0:
            # Try by MongoDB ObjectId
            try:
                res = self.courses.update_one({"_id": ObjectId(course_id), "modules.id": module_id}, {"$push": {"modules.$.lessons": lesson}})
            except Exception:
                return ""
        if res.modified_count > 0:
            return lesson["id"]
        return ""

    def upload_resource(self, course_id: str, module_id: str, lesson_id: str, resource: Dict[str, Any]) -> bool:
        # resource is a dict with keys like {"type":"video","url":"...","filename":"..."}
        # Query by id field (string) first
        res = self.courses.update_one(
            {"id": course_id, "modules.id": module_id, "modules.lessons.id": lesson_id},
            {"$push": {"modules.$[m].lessons.$[l].resources": resource}},
            array_filters=[{"m.id": module_id}, {"l.id": lesson_id}]
        )
        if res.matched_count == 0:
            # Try by MongoDB ObjectId
            try:
                res = self.courses.update_one(
                    {"_id": ObjectId(course_id), "modules.id": module_id, "modules.lessons.id": lesson_id},
                    {"$push": {"modules.$[m].lessons.$[l].resources": resource}},
                    array_filters=[{"m.id": module_id}, {"l.id": lesson_id}]
                )
            except Exception:
                return False
        return res.modified_count > 0

    def set_visibility(self, course_id: str, visibility: str) -> bool:
        if visibility not in ("draft", "published"):
            raise ValueError("status must be 'draft' or 'published'")
        # Try by string id first, then fall back to ObjectId
        res = self.courses.update_one({"id": course_id}, {"$set": {"status": visibility}})
        if res.matched_count == 0:
            try:
                res = self.courses.update_one({"_id": ObjectId(course_id)}, {"$set": {"status": visibility}})
            except Exception:
                return False
        return res.modified_count == 1

    def get_all_courses(self) -> List[Dict[str, Any]]:
        """Fetch all courses from the database"""
        return list(self.courses.find({}))

    def get_published_courses(self) -> List[Dict[str, Any]]:
        """Fetch only published courses"""
        return list(self.courses.find({"status": "published"}))

    def get_courses_by_instructor(self, instructor_id: str) -> List[Dict[str, Any]]:
        """Fetch courses taught by a specific instructor"""
        return list(self.courses.find({"instructorId": instructor_id}))

    def delete_module(self, course_id: str, module_id: str) -> bool:
        """Delete a module from a course"""
        # Try by string id first
        res = self.courses.update_one(
            {"id": course_id},
            {"$pull": {"modules": {"id": module_id}}}
        )
        if res.matched_count == 0:
            try:
                res = self.courses.update_one(
                    {"_id": ObjectId(course_id)},
                    {"$pull": {"modules": {"id": module_id}}}
                )
            except Exception:
                return False
        return res.modified_count > 0

    def delete_lesson(self, course_id: str, module_id: str, lesson_id: str) -> bool:
        """Delete a lesson from a module"""
        # Try by string id first
        res = self.courses.update_one(
            {"id": course_id, "modules.id": module_id},
            {"$pull": {"modules.$.lessons": {"id": lesson_id}}}
        )
        if res.matched_count == 0:
            try:
                res = self.courses.update_one(
                    {"_id": ObjectId(course_id), "modules.id": module_id},
                    {"$pull": {"modules.$.lessons": {"id": lesson_id}}}
                )
            except Exception:
                return False
        return res.modified_count > 0

