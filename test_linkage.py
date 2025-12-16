import sys
import os
from bson import ObjectId

# Add the project root to the python path
sys.path.append(os.getcwd())

from database.category_service import CategoryService
from database.course_service import CourseService

def test_linkage():
    print("Testing Category-Course Linkage...")
    
    course_service = CourseService()
    cat_service = CategoryService() # Reuse to verify side effects

    # 1. Create a course with a NEW category
    cat_name = "Artificial Intelligence"
    print(f"Creating course with new category: {cat_name}")
    # Fix: use keyword arg or positional if signature allows. create_course signature is (title, desc, instructor, category_name, ...)
    c1_id = course_service.create_course("AI Basics", "Intro to AI", "instAI", category_name=cat_name)
    
    # Verify Category Created
    cat = cat_service.get_category_by_name(cat_name)
    assert cat is not None
    print(f"Verified category '{cat_name}' created with ID: {cat['categoryId']}")
    
    # Verify Course linked in Category (ID list)
    assert c1_id in cat['courses']
    print("Verified course added to category's course list.")

    # Verify Course has correct categoryId
    course1 = course_service.get_course(c1_id)
    print(f"Course categoryId: {course1.get('categoryId')}")
    assert course1.get('categoryId') == cat['categoryId']

    # 2. Add another course to SAME category
    print("Creating second course in same category...")
    c2_id = course_service.create_course("Machine Learning", "ML Intro", "instAI", category_name=cat_name)
    
    # Verify link
    cat_updated = cat_service.get_category(cat['categoryId']) # Reload
    assert c2_id in cat_updated['courses']
    assert len(cat_updated['courses']) >= 2 
    print("Verified second course added to existing category.")

    # 3. Retrieve populated category to be sure
    cat_obj = cat_service.get_category_with_courses(cat['categoryId'])
    titles = [c.title for c in cat_obj.courses]
    assert "AI Basics" in titles
    assert "Machine Learning" in titles
    print(f"Verified populated category contains titles: {titles}")

    # Cleanup
    course_service.delete_course(c1_id)
    course_service.delete_course(c2_id)
    print("All linkage tests passed!")

if __name__ == "__main__":
    test_linkage()
