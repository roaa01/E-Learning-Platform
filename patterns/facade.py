from database.course_service import CourseService
from database.EnrollmentService import EnrollmentService
from database.assignment_service import AssignmentService
from database.seed import get_database

class StudentPortalFacade:
    """
    Facade Pattern: Provides a simplified interface for student-related operations.
    Hides the complexity of interacting with multiple services (Courses, Enrollments, Assignments).
    """

    def __init__(self):
        self.db = get_database()
        self.course_service = CourseService()
        self.enrollment_service = EnrollmentService(
            self.db.get_collection("enrollments"),
            self.db.get_collection("courses")
        )
        self.assignment_service = AssignmentService()

    def get_my_courses(self, user):
        """
        Get all courses the student is enrolled in.
        """
        return self.enrollment_service.get_enrolled_courses(user)

    def get_course_details(self, course_id):
        """
        Get full details for a specific course.
        """
        return self.course_service.get_course(course_id)

    def get_my_assignments(self, user):
        """
        Complex operation:
        1. Get all enrolled courses.
        2. Iterate through modules and lessons of each course.
        3. Find lessons of type 'assignment'.
        4. Fetch assignment details.
        5. Fetch student's submission status.
        6. Return a simplified list of assignment objects for the UI.
        """
        enrolled_courses = self.get_my_courses(user)
        assignments_data = []

        if not enrolled_courses:
            return []

        for course in enrolled_courses:
            course_id = course.get("courseId")
            course_title = course.get("title", "Unknown Course")
            
            # We need the full course object to get modules/lessons
            full_course = self.course_service.get_course(course_id)
            if not full_course:
                continue
            
            for module in full_course.get("modules", []):
                for lesson in module.get("lessons", []):
                    if lesson.get("type") == "assignment":
                        assignment_id = lesson.get("content")
                        if not assignment_id:
                            continue

                        # Fetch assignment details
                        assignment_doc = self.assignment_service.get_assignment(assignment_id)
                        
                        # Fetch submission status
                        submission = self.assignment_service.get_submission(assignment_id, str(user.id))
                        
                        # Flatten the data structure for the UI
                        assignments_data.append({
                            "course_title": course_title,
                            "assignment_id": assignment_id,
                            "title": assignment_doc.get("title", lesson.get("title", "Assignment")) if assignment_doc else lesson.get("title", "Assignment"),
                            "due_date": assignment_doc.get("dueDate") if assignment_doc else None,
                            "submission": submission,
                            "status": submission.get("status", "submitted") if submission else "pending",
                            "grade": submission.get("grade") if submission else None
                        })
        
        return assignments_data
