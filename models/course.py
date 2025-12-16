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


@dataclass
class Course:
    id: Optional[str] = None
    title: str = ""
    description: str = ""
    instructorId: Optional[str] = None
    categoryId: int = 0
    status: str = "draft"  # draft or published
    createdDate: datetime = field(default_factory=datetime.utcnow)
    modules: List[Module] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "instructorId": self.instructorId,
            "categoryId": self.categoryId,
            "createdDate": self.createdDate,
            "modules": [m.to_dict() for m in self.modules],
            "status": self.status,
        }

    def __str__(self):
        return f"Course(title={self.title}, modules={len(self.modules)})"
