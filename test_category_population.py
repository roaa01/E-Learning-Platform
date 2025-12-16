import sys
import os
from bson import ObjectId

# Add the project root to the python path
sys.path.append(os.getcwd())

from database.category_service import CategoryService
from database.course_service import CourseService
from models.course import Course
from models.category import Category

def test_category_population():
    print("Testing Category Population...")
    
    cat_service = CategoryService()
    course_service = CourseService()

    # 1. Create a Category
    cat_id = 888
    name = "Programming"
    desc = "Code courses"
    cat_service.create_category(cat_id, name, desc)

    # 2. Create and Add Courses
    c1_id = course_service.create_course("Python 101", "Intro", "inst1", category_name=name)
    c2_id = course_service.create_course("Java 101", "Intro", "inst1", category_name=name)
    print(f"Created courses: {c1_id}, {c2_id}")

    cat_service.add_course_to_category(cat_id, c1_id)
    cat_service.add_course_to_category(cat_id, c2_id)
    print("Added courses to category.")

    # 3. Retrieve with Population
    print("Retrieving category with courses...")
    category = cat_service.get_category_with_courses(cat_id)
    
    assert category is not None
    assert isinstance(category, Category)
    print(f"Retrieved Category: {category.name}")
    print(f"Number of courses: {len(category.courses)}")
    
    assert len(category.courses) == 2
    assert isinstance(category.courses[0], Course)
    
    titles = [c.title for c in category.courses]
    assert "Python 101" in titles
    assert "Java 101" in titles
    print(f"Found titles: {titles}")

    # Cleanup
    course_service.delete_course(c1_id)
    course_service.delete_course(c2_id)
    print("Test passed!")

if __name__ == "__main__":
    test_category_population()
