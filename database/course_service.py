from typing import Optional, Dict, Any, List
from bson import ObjectId
from datetime import datetime
from .seed import get_database
from models.course import Course, Module, Lesson


class CourseService:
    def __init__(self):
        self.db = get_database()
        self.courses = self.db.get_collection("courses")

    def create_course(self, title: str, description: str, instructor_id: str, category: str = "", visibility: str = "draft") -> str:
        # Use UML attribute names: id, instructorId, createdDate, status
        new_id = str(ObjectId())
        course_doc = {
            "id": new_id,
            "title": title,
            "description": description,
            "instructorId": instructor_id,
            "category": category,
            "status": visibility,
            "createdDate": datetime.utcnow(),
            "modules": [],
        }
        res = self.courses.insert_one(course_doc)
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
        res = self.courses.delete_one({"_id": ObjectId(course_id)})
        return res.deleted_count == 1

    def update_course(self, course_id: str, updates: Dict[str, Any]) -> bool:
        if "modules" in updates:
            # ensure modules structure is serializable
            updates["modules"] = [m if isinstance(m, dict) else m.to_dict() for m in updates["modules"]]
        # Try to update by ObjectId first, fall back to id field
        try:
            res = self.courses.update_one({"_id": ObjectId(course_id)}, {"$set": updates})
        except Exception:
            res = self.courses.update_one({"id": course_id}, {"$set": updates})
        return res.modified_count == 1

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
        try:
            res = self.courses.update_one({"_id": ObjectId(course_id)}, {"$set": {"status": visibility}})
        except Exception:
            res = self.courses.update_one({"id": course_id}, {"$set": {"status": visibility}})
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
