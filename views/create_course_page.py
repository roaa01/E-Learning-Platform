import customtkinter as ctk
from database.course_service import CourseService


class CreateCoursePage(ctk.CTkFrame):
    """Page for instructors to create new courses"""
    
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
            text="Create New Course",
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
           
        
        
        # Scrollable form container
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        # Form fields
        form_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        # Course Title
        title_label = ctk.CTkLabel(form_frame, text="Course Title:", font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=(10, 5))
        self.title_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter course title")
        self.title_entry.pack(fill="x", pady=5)
        
        # Course Description
        desc_label = ctk.CTkLabel(form_frame, text="Description:", font=("Arial", 12, "bold"))
        desc_label.pack(anchor="w", pady=(10, 5))
        self.desc_entry = ctk.CTkTextbox(form_frame, height=100)
        self.desc_entry.pack(fill="x", pady=5)
        
        # Category
        category_label = ctk.CTkLabel(form_frame, text="Category:", font=("Arial", 12, "bold"))
        category_label.pack(anchor="w", pady=(10, 5))
        self.category_combo = ctk.CTkComboBox(
            form_frame,
            values=["Programming", "Web Development", "Data Science", "Design", "Business", "Other"],
            state="readonly"
        )
        self.category_combo.pack(fill="x", pady=5)
        self.category_combo.set("Programming")
        
        # Course Status
        status_label = ctk.CTkLabel(form_frame, text="Status:", font=("Arial", 12, "bold"))
        status_label.pack(anchor="w", pady=(10, 5))
        self.status_combo = ctk.CTkComboBox(
            form_frame,
            values=["published","draft"],
            state="readonly"
        )
        self.status_combo.pack(fill="x", pady=5)
        self.status_combo.set("published")
        
        # Message Label
        self.message_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=("Arial", 12),
            text_color="gray"
        )
        self.message_label.pack(pady=20)
        
        # Buttons Frame
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        create_btn = ctk.CTkButton(
            btn_frame,
            text="Create Course",
            command=self.handle_create_course,
            fg_color="green",
            hover_color="darkgreen"
        )
        create_btn.pack(side="left", padx=10)
        
        reset_btn = ctk.CTkButton(
            btn_frame,
            text="Reset",
            command=self.handle_reset,
            fg_color="gray"
        )
        reset_btn.pack(side="left", padx=10)
    
    def handle_create_course(self):
        """Create a new course"""
        title = self.title_entry.get().strip()
        description = self.desc_entry.get("1.0", "end").strip()
        category = self.category_combo.get()
        status = self.status_combo.get()
        
        # Validation
        if not title:
            self.show_message("Please enter a course title", "red")
            return
        
        if not description:
            self.show_message("Please enter a description", "red")
            return
        
        try:
            # Get the current instructor's ID from the logged-in user
            user = self.page_manager.get_user()
            instructor_id = str(user.id)
            
            # Create course
            course_id = self.course_service.create_course(
                title=title,
                description=description,
                instructor_id=instructor_id,
                category_name=category,
                visibility=status
            )
            
            if course_id:
                self.show_message(f"Course '{title}' created successfully!", "green")
                self.clear_form()
                # Navigate to manage course page to add modules/lessons
                manage_page = self.page_manager.get_page("manage_course")
                manage_page.set_course(course_id)
                self.page_manager.show_page("manage_course")
            else:
                self.show_message("Failed to create course", "red")
        
        except Exception as e:
            self.show_message(f"Error: {str(e)}", "red")
            print(f"Course creation error: {e}")
    
    def handle_reset(self):
        """Reset the form"""
        self.clear_form()
        self.show_message("Form reset", "gray")
    
    def clear_form(self):
        """Clear all form fields"""
        self.title_entry.delete(0, "end")
        self.desc_entry.delete("1.0", "end")
        self.category_combo.set("Programming")
        self.status_combo.set("draft")
    
    def show_message(self, message: str, color: str):
        """Display a message to the user"""
        self.message_label.configure(text=message, text_color=color)
    
    def go_back(self):
        """Go back to dashboard"""
        self.page_manager.show_page("dashboard")
