import sys
import os
from bson import ObjectId

# Add the project root to the python path
sys.path.append(os.getcwd())

from database.category_service import CategoryService
from database.course_service import CourseService

def test_category_persistence():
    print("Testing Category Persistence...")
    
    cat_service = CategoryService()
    course_service = CourseService()

    # 1. Create a Category
    cat_id = 999
    name = "Test Category"
    desc = "Testing persistence"
    
    print(f"Creating category {cat_id}...")
    success = cat_service.create_category(cat_id, name, desc)
    if success:
        print("Category created successfully.")
    else:
        print("Failed to create category (might already exist).")

    # 2. Retrieve Category
    cat = cat_service.get_category(cat_id)
    assert cat is not None
    assert cat['name'] == name
    print(f"Retrieved category: {cat['name']}")

    # 3. Add Course to Category
    # Create a dummy course first
    course_id = course_service.create_course("Test Course for Cat", "Desc", "instructor123", category_name="Test Category")
    print(f"Created course with ID: {course_id}")

    print("Adding course to category...")
    cat_service.add_course_to_category(cat_id, course_id)
    
    cat = cat_service.get_category(cat_id)
    assert course_id in cat['courses']
    print(f"Course {course_id} found in category courses.")

    # 4. Remove Course
    print("Removing course from category...")
    cat_service.remove_course_from_category(cat_id, course_id)
    
    cat = cat_service.get_category(cat_id)
    assert course_id not in cat['courses']
    print("Course removed successfully.")

    # Cleanup (Optional: delete the test category/course)
    course_service.delete_course(course_id)
    # No delete method for category in service yet, but that's fine for now.

    print("All persistence tests passed!")

if __name__ == "__main__":
    test_category_persistence()
