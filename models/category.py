from dataclasses import dataclass, field
from typing import List
from models.course import Course

@dataclass
class Category:
    categoryId: int
    name: str
    description: str
    courses: List[Course] = field(default_factory=list)

    def addCourse(self, course: Course):
        if course not in self.courses:
            self.courses.append(course)

    def removeCourse(self, course: Course):
        if course in self.courses:
            self.courses.remove(course)

    def getCourses(self) -> List[Course]:
        return self.courses

    def to_dict(self):
        return {
            "categoryId": self.categoryId,
            "name": self.name,
            "description": self.description,
            "courses": [c.id for c in self.courses if c.id] # Store only IDs to avoid circularity/duplication in DB
        }
