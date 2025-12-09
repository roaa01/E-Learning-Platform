# models/course.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


class Lesson:
     def __init__(self, id,moduleId,title, content,type):
        self.title = title
        self.content = conten
        self.id = id
        self.moduleId = moduleId
        self.type = type
class Module:
    def __init__(self, id,courseId,title, lessons: Optional[List[Lesson]] = None):
        self.id = id
        self.courseId = courseId
        self.title = title
        self.lessons = lessons if lessons is not None else []
class Course:
    def __init__(self, id,title, description,instructorId,category,createdDate, modules: Optional[List[Module]] = None):
        self.id = id
        self.instructorId = instructorId
        self.category = category
        self.createdDate = createdDate
        self.title = title
        self.description = description
        self.modules = modules if modules is not None else []

    def __str__(self):
        return f"Course(title={self.title}, modules={len(self.modules)})"
