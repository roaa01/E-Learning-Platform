"""
Debug script to check what's in the database
"""
from database.seed import get_database
from bson import ObjectId

def check_database():
    db = get_database()
    enrollments = db.get_collection("enrollments")
    courses = db.get_collection("courses")
    
    print("=== COURSES ===")
    for course in courses.find():
        print(f"_id: {course.get('_id')}, id: {course.get('id')}, title: {course.get('title')}")
    
    print("\n=== ENROLLMENTS ===")
    for enrollment in enrollments.find():
        print(f"_id: {enrollment.get('_id')}")
        print(f"  student_id: {enrollment.get('student_id')} (type: {type(enrollment.get('course_id')).__name__})")
        print(f"  course_id: {enrollment.get('course_id')} (type: {type(enrollment.get('course_id')).__name__})")
        print(f"  status: {enrollment.get('status')}")
        print()

if __name__ == "__main__":
    check_database()
