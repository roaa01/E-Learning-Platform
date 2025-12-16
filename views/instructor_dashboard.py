"""
Instructor Dashboard and Enrollment Requests Page
Consolidated from dashboard_page.py (instructor content) and enrollment_requests_page.py
"""
import customtkinter as ctk
from database.EnrollmentService import EnrollmentService
from database.course_service import CourseService
from database.seed import get_database


class InstructorDashboard(ctk.CTkFrame):
    """Instructor dashboard with navigation buttons"""
    
    def __init__(self, master, page_manager):
        super().__init__(master)
        self.page_manager = page_manager
        
    def on_show(self):
        """Refresh dashboard content when shown"""
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()
        
    def create_widgets(self):
        user = self.page_manager.get_user()
        
        # Welcome Section
        welcome_frame = ctk.CTkFrame(self)
        welcome_frame.pack(pady=30, padx=30, fill="x")
        
        display_name = getattr(user, 'full_name', None) or getattr(user, 'username', None) or getattr(user, 'name', None) or str(user)
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text=f"Welcome, {display_name}!",
            font=("Arial", 28, "bold")
        )
        welcome_label.pack(pady=10)

        role_label = ctk.CTkLabel(
            welcome_frame,
            text="Role: Instructor",
            font=("Arial", 16)
        )
        role_label.pack(pady=5)

        email = getattr(user, 'email', None)
        if email:
            email_label = ctk.CTkLabel(
                welcome_frame,
                text=f"Email: {email}",
                font=("Arial", 14),
                text_color="gray"
            )
            email_label.pack(pady=5)

        # Main Content Area
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(pady=20, padx=30, fill="both", expand=True)

        content_title = ctk.CTkLabel(
            content_frame,
            text="Instructor Dashboard",
            font=("Arial", 20, "bold")
        )
        content_title.pack(pady=20)
        
        info = ctk.CTkLabel(
            content_frame,
            text="Manage your courses and students.",
            font=("Arial", 14)
        )
        info.pack(pady=10)
        
        # Navigation buttons
        btn_frame = ctk.CTkFrame(content_frame)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="My Courses", 
            command=self.show_my_courses
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Create Course", 
            command=lambda: self.page_manager.show_page("create_course")
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Student Analytics"
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Enrollment Requests", 
            command=lambda: self.page_manager.show_page("enrollment_requests")
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="View All Courses", 
            command=self.show_all_courses
        ).pack(pady=5)

        # Logout Button
        logout_btn = ctk.CTkButton(
            self,
            text="Logout",
            command=self.handle_logout,
            fg_color="red",
            hover_color="darkred"
        )
        logout_btn.pack(pady=20)
        
    def show_all_courses(self):
        courses_page = self.page_manager.get_page("courses")
        courses_page.set_mode("all")
        self.page_manager.show_page("courses")

    def show_my_courses(self):
        user = self.page_manager.get_user()
        if user:
            # Robust ID extraction
            uid = getattr(user, 'id', None)
            if not uid:
                uid = getattr(user, '_id', None)
            uid = str(uid) if uid else ""
            
            print(f"[Dashboard] Filtering courses for instructor_id: {uid}")
            courses_page = self.page_manager.get_page("courses")
            courses_page.set_mode("instructor", uid)
            self.page_manager.show_page("courses")
        
    def handle_logout(self):
        self.page_manager.set_user(None)
        self.page_manager.show_page("auth")


class EnrollmentRequestsPage(ctk.CTkFrame):
    """Page for instructors to view and manage all enrollment requests"""
    
    def __init__(self, master, page_manager):
        super().__init__(master)
        self.page_manager = page_manager
        
        db = get_database()
        self.enrollment_service = EnrollmentService(
            db.get_collection("enrollments"),
            db.get_collection("courses")
        )
        self.course_service = CourseService()
        
    def on_show(self):
        """Refresh content when page is shown"""
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(pady=20, padx=30, fill="x")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Enrollment Requests",
            font=("Arial", 24, "bold")
        )
        title_label.pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="Refresh",
            command=self.on_show,
            width=80
        )
        refresh_btn.pack(side="right", padx=5)
        
        back_btn = ctk.CTkButton(
            header_frame,
            text="Back",
            command=self.go_back,
            width=80
        )
        back_btn.pack(side="right")
        
        # Scrollable requests container
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        # Get instructor's courses
        user = self.page_manager.get_user()
        if not user or user.role != "instructor":
            ctk.CTkLabel(scroll_frame, text="Access denied", text_color="red").pack(pady=20)
            return
            
        instructor_id = str(user.id)
        courses = self.course_service.get_courses_by_instructor(instructor_id)
        
        print(f"[DEBUG] Instructor ID: {instructor_id}")
        print(f"[DEBUG] Found {len(courses)} courses for instructor")
        
        if not courses:
            ctk.CTkLabel(scroll_frame, text="You don't have any courses yet.", text_color="gray").pack(pady=20)
            return
        
        # Get pending enrollments for each course
        total_requests = 0
        for course in courses:
            course_id = course.get("id")
            print(f"[DEBUG] Checking course: {course.get('title')} (id: {course_id})")
            requests = self.enrollment_service.get_pending_enrollments(course_id)
            print(f"[DEBUG] Found {len(requests)} pending requests for course {course_id}")
            
            if requests:
                total_requests += len(requests)
                # Course header
                course_frame = ctk.CTkFrame(scroll_frame, fg_color="gray15")
                course_frame.pack(fill="x", pady=10, padx=0)
                
                ctk.CTkLabel(
                    course_frame,
                    text=f"📚 {course.get('title', 'Untitled Course')}",
                    font=("Arial", 16, "bold"),
                    text_color="lightblue"
                ).pack(anchor="w", padx=15, pady=(10, 5))
                
                ctk.CTkLabel(
                    course_frame,
                    text=f"{len(requests)} pending request(s)",
                    font=("Arial", 11),
                    text_color="orange"
                ).pack(anchor="w", padx=15, pady=(0, 10))
                
                # List requests
                for req in requests:
                    self.create_request_card(course_frame, req, course_id)
        
        if total_requests == 0:
            ctk.CTkLabel(
                scroll_frame,
                text="No pending enrollment requests",
                font=("Arial", 14),
                text_color="gray"
            ).pack(pady=20)
    
    def create_request_card(self, parent, request, course_id):
        """Create a card for a single enrollment request"""
        card = ctk.CTkFrame(parent, fg_color="gray20", border_width=1, border_color="gray30")
        card.pack(fill="x", pady=5, padx=15)
        
        # Student info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"👤 {request.get('student_name', 'Unknown')}",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=request.get('student_email', ''),
            font=("Arial", 10),
            text_color="gray"
        ).pack(anchor="w")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=15, pady=10)
        
        def approve():
            enrollment_id = request.get("enrollment_id")
            if self.enrollment_service.approve_enrollment(enrollment_id):
                card.destroy()
                self.show_message("Enrollment approved!", "green")
            else:
                self.show_message("Failed to approve enrollment", "red")
        
        def reject():
            enrollment_id = request.get("enrollment_id")
            if self.enrollment_service.reject_enrollment(enrollment_id):
                card.destroy()
                self.show_message("Enrollment rejected", "orange")
            else:
                self.show_message("Failed to reject enrollment", "red")
        
        ctk.CTkButton(
            btn_frame,
            text="✓ Approve",
            command=approve,
            fg_color="green",
            hover_color="darkgreen",
            width=90,
            height=30
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="✗ Reject",
            command=reject,
            fg_color="red",
            hover_color="darkred",
            width=90,
            height=30
        ).pack(side="left", padx=5)
    
    def show_message(self, message, color):
        """Show a temporary message"""
        print(f"[{color.upper()}] {message}")
    
    def go_back(self):
        """Go back to dashboard"""
        self.page_manager.show_page("dashboard")
