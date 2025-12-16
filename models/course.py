from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


@dataclass
class Lesson:
    id: Optional[str] = None
    title: str = ""
    content: str = ""
    type: str = ""
    resources: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "type": self.type,
            "resources": self.resources,
        }
    

@dataclass
class Module:
    id: Optional[str] = None
    title: str = ""
    lessons: List[Lesson] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "lessons": [l.to_dict() for l in self.lessons],
        }

    def get_lesson_count(self) -> int:
        return len(self.lessons)

@dataclass
class Course:
    id: Optional[str] = None
    title: str = ""
    description: str = ""
    instructor_id: Optional[str] = None
    category_id: int = 0
    status: str = "draft"  # draft or published
    # New fields
    level: str = "Beginner" # Beginner, Intermediate, Advanced
    price: float = 0.0
    created_date: datetime = field(default_factory=datetime.utcnow)
    modules: List[Module] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "instructorId": self.instructor_id,
            "categoryId": self.category_id,
            "level": self.level,
            "price": self.price,
            "createdDate": self.created_date,
            "modules": [m.to_dict() for m in self.modules],
            "status": self.status,
        }

    def is_published(self) -> bool:
        return self.status == "published"

    def is_draft(self) -> bool:
        return self.status == "draft"

    def get_module_count(self) -> int:
        return len(self.modules)

    def get_lesson_count(self) -> int:
        return sum(module.get_lesson_count() for module in self.modules)

    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}', status='{self.status}', modules={len(self.modules)})>"
