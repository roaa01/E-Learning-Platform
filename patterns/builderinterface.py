from abc import ABC, abstractmethod

class CourseBuilder(ABC):
    @abstractmethod
    def set_title(self, title: str):
        pass

    @abstractmethod
    def set_description(self, description: str):
        pass

    @abstractmethod
    def set_instructor(self, instructorId: str):
        pass

    @abstractmethod
    def set_category(self, category: str):
        pass

    @abstractmethod
    def add_module(self, module_title: str):
        pass

    @abstractmethod
    def add_lesson_to_module(self, module_index: int, lesson_title: str, lesson_content: str, lesson_type: str):
        pass

    @abstractmethod
    def build(self):
        pass
