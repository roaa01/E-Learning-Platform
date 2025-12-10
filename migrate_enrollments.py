"""
Migration script to convert enrollment course_id from ObjectId to string format
Run this once to fix existing enrollments in the database
"""
from database.seed import get_database
from bson import ObjectId

def migrate_enrollments():
    db = get_database()
    enrollments = db.get_collection("enrollments")
    
    # Find all enrollments where course_id is an ObjectId
    cursor = enrollments.find({"course_id": {"$type": "objectId"}})
    
    count = 0
    for enrollment in cursor:
        course_oid = enrollment["course_id"]
        
        # Convert ObjectId to string
        course_id_str = str(course_oid)
        
        # Update the enrollment to use string course_id
        enrollments.update_one(
            {"_id": enrollment["_id"]},
            {"$set": {"course_id": course_id_str}}
        )
        count += 1
        print(f"✓ Migrated enrollment {enrollment['_id']}: course_id ObjectId({course_oid}) → '{course_id_str}'")
    
    print(f"\n✓ Migration complete! Updated {count} enrollment(s)")

if __name__ == "__main__":
    migrate_enrollments()
