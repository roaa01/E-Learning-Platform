from .builderinterface import CourseBuilder
from models.course import Course, Module, Lesson
from datetime import datetime


class ConcreteCourseBuilder(CourseBuilder):
    def __init__(self):
        self.reset()

    def reset(self):
        self.course = Course(id=None, title="", description="", instructorId=None, category="", createdDate=datetime.utcnow())

    def set_title(self, title: str):
        self.course.title = title
        return self

    def set_description(self, description: str):
        self.course.description = description
        return self

    def set_instructor(self, instructorId: str):
        self.course.instructor_id = instructorId
        return self

    def set_category(self, category: str):
        self.course.category = category
        return self

    def add_module(self, module_title: str):
        module = Module(id=None, title=module_title)
        self.course.modules.append(module)
        return self

    def add_lesson_to_module(self, module_index: int, lesson_title: str, lesson_content: str, lesson_type: str):
        if module_index < len(self.course.modules):
            lesson = Lesson(id=None, title=lesson_title, content=lesson_content, type=lesson_type)
            self.course.modules[module_index].lessons.append(lesson)
        else:
            raise IndexError("Module index does not exist")
        return self

    def build(self):
        built_course = self.course
        self.reset()  # optional: reset builder to build a new course
        return built_course
