import customtkinter as ctk
from database.EnrollmentService import EnrollmentService
from database.seed import get_database

class EnrollmentRequestsPage(ctk.CTkFrame):
    def __init__(self, master, page_manager):
        super().__init__(master)
        self.page_manager = page_manager
        db = get_database()
        self.enrollment_service = EnrollmentService(
            db.get_collection("enrollments"),
            db.get_collection("courses")
        )
        self.create_widgets()

    def create_widgets(self):
        user = self.page_manager.get_user()
        instructor_id = str(getattr(user, 'id', getattr(user, '_id', None)))
        # Find all pending enrollments for this instructor's courses
        pending = list(self.enrollment_service.enrollments.aggregate([
            {"$match": {"status": "pending"}},
            {"$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "_id",
                "as": "course"
            }},
            {"$unwind": "$course"},
            {"$match": {"course.instructorId": instructor_id}}
        ]))
        # Display
        for req in pending:
            frame = ctk.CTkFrame(self)
            frame.pack(fill="x", pady=5, padx=10)
            ctk.CTkLabel(frame, text=f"Student: {req.get('student_id')} | Course: {req['course'].get('title')}").pack(side="left")
            approve_btn = ctk.CTkButton(frame, text="Approve", fg_color="green", command=lambda rid=req['_id']: self.approve(rid))
            approve_btn.pack(side="right")

    def approve(self, enrollment_id):
        ok = self.enrollment_service.approve_enrollment(str(enrollment_id))
        if ok:
            self.create_widgets()  # Refresh