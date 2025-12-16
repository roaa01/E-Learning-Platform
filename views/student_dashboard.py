"""
Student Dashboard and My Courses Page
Consolidated from dashboard_page.py (student content) and student_courses.py
"""
import customtkinter as ctk
from tkinter import messagebox
from database.EnrollmentService import EnrollmentService
from database.course_service import CourseService
from database.seed import get_database
from views.assignment_view import AssignmentView


class StudentDashboard(ctk.CTkFrame):
    """Student dashboard with navigation buttons"""
    
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
            text="Role: Student",
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
            text="Student Dashboard",
            font=("Arial", 20, "bold")
        )
        content_title.pack(pady=20)
        
        info = ctk.CTkLabel(
            content_frame,
            text="Your enrolled courses will appear here.",
            font=("Arial", 14)
        )
        info.pack(pady=10)
        
        # Navigation buttons
        btn_frame = ctk.CTkFrame(content_frame)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="Browse Courses", 
            command=self.show_all_courses
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="My Enrolled Courses", 
            command=lambda: self.page_manager.show_page("my_courses")
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="My Progress"
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Assignments"
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
        
    def handle_logout(self):
        self.page_manager.set_user(None)
        self.page_manager.show_page("auth")


class MyCoursesPage(ctk.CTkFrame):
    """Page for students to view their enrolled (approved) courses"""
    
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
            text="My Enrolled Courses",
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
        
        # Scrollable courses container
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        # Fetch enrolled courses
        user = self.page_manager.get_user()
        courses = self.enrollment_service.get_enrolled_courses(user)
        
        if not courses:
            no_courses_label = ctk.CTkLabel(
                scroll_frame,
                text="You are not enrolled in any courses yet.\n\nBrowse available courses to get started!",
                font=("Arial", 14),
                text_color="gray"
            )
            no_courses_label.pack(pady=20)
            
            browse_btn = ctk.CTkButton(
                scroll_frame,
                text="Browse Courses",
                command=lambda: self.page_manager.show_page("courses"),
                width=150,
                fg_color="green",
                hover_color="darkgreen"
            )
            browse_btn.pack(pady=10)
        else:
            # Display enrolled courses
            courses_count_label = ctk.CTkLabel(
                scroll_frame,
                text=f"You are enrolled in {len(courses)} course(s)",
                font=("Arial", 12),
                text_color="lightgreen"
            )
            courses_count_label.pack(pady=(0, 15), anchor="w")
            
            for course in courses:
                self.create_course_card(scroll_frame, course)
    
    def create_course_card(self, parent, course):
        """Create a card widget for an enrolled course"""
        card = ctk.CTkFrame(parent, fg_color="gray20", border_width=2, border_color="green")
        card.pack(pady=10, padx=0, fill="x")
        
        # Course Title
        title = ctk.CTkLabel(
            card,
            text=course.get("title", "Untitled Course"),
            font=("Arial", 16, "bold")
        )
        title.pack(pady=(15, 5), padx=15, anchor="w")
        
        # Enrollment status badge
        status_badge = ctk.CTkLabel(
            card,
            text="✓ Enrolled",
            font=("Arial", 10, "bold"),
            text_color="lightgreen",
            fg_color="darkgreen",
            corner_radius=5
        )
        status_badge.pack(pady=5, padx=15, anchor="w")
        
        # Course Description
        desc = ctk.CTkLabel(
            card,
            text=course.get("description", "No description available"),
            font=("Arial", 12),
            text_color="gray",
            wraplength=500,
            justify="left"
        )
        desc.pack(pady=5, padx=15, anchor="w")
        
        # Course Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(pady=5, padx=15, fill="x")
        
        category = course.get("category", "N/A")
        category_label = ctk.CTkLabel(
            info_frame,
            text=f"📚 Category: {category}",
            font=("Arial", 11),
            text_color="lightblue"
        )
        category_label.pack(side="left", padx=5)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=(5, 15), padx=15, anchor="e")
        
        # View Course Button
        view_btn = ctk.CTkButton(
            btn_frame,
            text="Open Course",
            command=lambda: self.open_course(course.get("course_id")),
            width=120,
            height=30,
            fg_color="blue",
            hover_color="darkblue"
        )
        view_btn.pack(side="left", padx=5)
        
        # View Progress Button
        progress_btn = ctk.CTkButton(
            btn_frame,
            text="My Progress",
            command=lambda: self.view_progress(course),
            width=120,
            height=30
        )
        progress_btn.pack(side="left", padx=5)
    
    def open_course(self, course_id):
        """Open the course content/modules in a dialog"""
        course = self.course_service.get_course(course_id)
        if not course:
            messagebox.showerror("Error", "Course not found")
            return
            
        dlg = ctk.CTkToplevel(self)
        dlg.title(course.get("title", "Course Details"))
        dlg.geometry("700x600")

        header = ctk.CTkFrame(dlg)
        header.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(header, text=course.get("title", ""), font=("Arial", 18, "bold")).pack(anchor="w")
        ctk.CTkLabel(header, text=f"Category: {course.get('category','N/A')}", text_color="gray").pack(anchor="w")

        body = ctk.CTkScrollableFrame(dlg)
        body.pack(fill="both", expand=True, padx=12, pady=(0,12))

        # Description
        ctk.CTkLabel(body, text="Description:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(6,2))
        ctk.CTkLabel(body, text=course.get("description", ""), wraplength=640, text_color="gray").pack(anchor="w", pady=(0,8))

        # Modules and lessons
        modules = course.get("modules", [])
        if not modules:
            ctk.CTkLabel(body, text="No modules yet", text_color="gray").pack(pady=10)
        else:
            for m in modules:
                m_frame = ctk.CTkFrame(body, fg_color="gray20")
                m_frame.pack(fill="x", pady=6)
                ctk.CTkLabel(m_frame, text=m.get("title","Module"), font=("Arial", 12, "bold")).pack(anchor="w", padx=8, pady=(6,2))
                for l in m.get("lessons", []):
                    lesson_frame = ctk.CTkFrame(m_frame, fg_color="transparent")
                    lesson_frame.pack(fill="x", padx=18, pady=2)
                    
                    lesson_text = f"- {l.get('title','Lesson')} ({l.get('type','')})"
                    ctk.CTkLabel(lesson_frame, text=lesson_text, wraplength=450).pack(side="left")
                    
                    if l.get("type") == "assignment":
                        assign_id = l.get("content") # content holds the assignment_id
                        if assign_id:
                            # Small button to open assignment
                            ctk.CTkButton(
                                lesson_frame, 
                                text="Open Assignment", 
                                width=120, 
                                height=24,
                                fg_color="orange", 
                                command=lambda aid=assign_id: AssignmentView(self, aid, str(self.page_manager.get_user().id))
                            ).pack(side="right", padx=10)

                        # show resources (if any)
                        resources = l.get("resources", [])
                        if resources:
                            for r in resources:
                                rtxt = f"   • [{r.get('type','')}] {r.get('name','')} - {r.get('url','') or ''}"
                                ctk.CTkLabel(m_frame, text=rtxt, text_color="gray", wraplength=620).pack(anchor="w", padx=28, pady=(0,2))

        # Footer
        footer = ctk.CTkFrame(dlg)
        footer.pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(footer, text="Close", command=dlg.destroy).pack(side="right", padx=6)
    
    def view_progress(self, course):
        """View student's progress in the course"""
        # TODO: Implement progress tracking
        messagebox.showinfo(
            "Course Progress",
            f"Progress for: {course.get('title')}\n\n(Progress tracking coming soon!)"
        )
    
    def go_back(self):
        """Go back to dashboard"""
        self.page_manager.show_page("dashboard")
