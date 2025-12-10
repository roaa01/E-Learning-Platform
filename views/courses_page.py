import customtkinter as ctk
from database.course_service import CourseService


class CoursesPage(ctk.CTkFrame):
    """Page to display all available courses"""
    
    def __init__(self, master, page_manager):
        super().__init__(master)
        self.page_manager = page_manager
        self.course_service = CourseService()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(pady=20, padx=30, fill="x")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Available Courses",
            font=("Arial", 24, "bold")
        )
        title_label.pack(side="left")
        
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
        
        # Fetch and display courses
        courses = self.course_service.get_published_courses()
        
        if not courses:
            no_courses_label = ctk.CTkLabel(
                scroll_frame,
                text="No courses available yet.",
                font=("Arial", 14),
                text_color="gray"
            )
            no_courses_label.pack(pady=20)
        else:
            for course in courses:
                self.create_course_card(scroll_frame, course)
    
    def create_course_card(self, parent, course):
        """Create a card widget for a single course"""
        card = ctk.CTkFrame(parent, fg_color="gray20")
        card.pack(pady=10, padx=0, fill="x")
        
        # Course Title
        title = ctk.CTkLabel(
            card,
            text=course.get("title", "Untitled Course"),
            font=("Arial", 16, "bold")
        )
        title.pack(pady=(10, 5), padx=15, anchor="w")
        
        # Course Description
        desc = ctk.CTkLabel(
            card,
            text=course.get("description", "No description"),
            font=("Arial", 12),
            text_color="gray",
            wraplength=400
        )
        desc.pack(pady=5, padx=15, anchor="w")
        
        # Course Info (Category, Modules count)
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(pady=5, padx=15, fill="x")
        
        category = ctk.CTkLabel(
            info_frame,
            text=f"Category: {course.get('category', 'N/A')}",
            font=("Arial", 11),
            text_color="lightblue"
        )
        category.pack(side="left", padx=5)
        
        modules_count = len(course.get("modules", []))
        modules_label = ctk.CTkLabel(
            info_frame,
            text=f"Modules: {modules_count}",
            font=("Arial", 11),
            text_color="lightgreen"
        )
        modules_label.pack(side="left", padx=5)
        
        # Enroll Button
        enroll_btn = ctk.CTkButton(
            card,
            text="View Course",
            command=lambda: self.view_course_details(course.get("id")),
            width=120,
            height=30
        )
        enroll_btn.pack(pady=(5, 10), padx=15, anchor="e")
    
    def view_course_details(self, course_id):
        """Handle viewing course details (placeholder for now)"""
        print(f"Viewing course: {course_id}")
        # TODO: Implement course detail page
    
    def go_back(self):
        """Go back to dashboard"""
        self.page_manager.show_page("dashboard")
