from dataclasses import dataclass, field
from typing import List
from models.course import Course

@dataclass
class Category:
    category_id: int
    name: str
    description: str
    courses: List[Course] = field(default_factory=list)

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "categoryId": self.category_id,
            "name": self.name,
            "description": self.description,
            "courses": [c.id for c in self.courses if c.id] # Store only IDs
        }

    def add_course(self, course: Course):
        """Add a course to this category"""
        if course not in self.courses:
            self.courses.append(course)

    def remove_course(self, course: Course):
        """Remove a course from this category"""
        if course in self.courses:
            self.courses.remove(course)

    def get_courses(self) -> List[Course]:
        """Get all courses in this category"""
        return self.courses

    def get_course_count(self) -> int:
        """Get number of courses in this category"""
        return len(self.courses)


