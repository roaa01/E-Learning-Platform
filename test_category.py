import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

from models.category import Category
from models.course import Course

def test_category():
    print("Testing Category Class...")
    
    # Create courses
    c1 = Course(title="Python Basics")
    c2 = Course(title="Advanced Python")
    
    # Create category
    cat = Category(categoryId=1, name="Programming", description="Coding courses")
    print(f"Created Category: {cat.name}")

    # Test addCourse
    cat.addCourse(c1)
    cat.addCourse(c2)
    print(f"Added 2 courses. Count: {len(cat.getCourses())}")
    assert len(cat.getCourses()) == 2
    assert c1 in cat.getCourses()
    assert c2 in cat.getCourses()

    # Test removeCourse
    cat.removeCourse(c1)
    print(f"Removed 1 course. Count: {len(cat.getCourses())}")
    assert len(cat.getCourses()) == 1
    assert c1 not in cat.getCourses()
    assert c2 in cat.getCourses()

    print("All tests passed!")

if __name__ == "__main__":
    test_category()
