import customtkinter as ctk

class DashboardPage(ctk.CTkFrame):
    """Dashboard page shown after successful login/signup"""
    
    def __init__(self, master, page_manager):
        super().__init__(master)
        self.page_manager = page_manager
        
        self.create_widgets()
        
    def create_widgets(self):
        user = self.page_manager.get_user()
        
        # Welcome Section
        welcome_frame = ctk.CTkFrame(self)
        welcome_frame.pack(pady=30, padx=30, fill="x")
        
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text=f"Welcome, {user.name}!",
            font=("Arial", 28, "bold")
        )
        welcome_label.pack(pady=10)
        
        role_label = ctk.CTkLabel(
            welcome_frame,
            text=f"Role: {user.role.capitalize()}",
            font=("Arial", 16)
        )
        role_label.pack(pady=5)
        
        email_label = ctk.CTkLabel(
            welcome_frame,
            text=f"Email: {user.email}",
            font=("Arial", 14),
            text_color="gray"
        )
        email_label.pack(pady=5)
        
        # Main Content Area
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        content_title = ctk.CTkLabel(
            content_frame,
            text="Dashboard",
            font=("Arial", 20, "bold")
        )
        content_title.pack(pady=20)
        
        # Role-specific content
        if user.role == "student":
            self.create_student_content(content_frame)
        elif user.role == "instructor":
            self.create_instructor_content(content_frame)
        elif user.role == "admin":
            self.create_admin_content(content_frame)
        
        # Logout Button
        logout_btn = ctk.CTkButton(
            self,
            text="Logout",
            command=self.handle_logout,
            fg_color="red",
            hover_color="darkred"
        )
        logout_btn.pack(pady=20)
        
    def create_student_content(self, parent):
        info = ctk.CTkLabel(
            parent,
            text="Student Dashboard\n\nYour enrolled courses will appear here.",
            font=("Arial", 14)
        )
        info.pack(pady=20)
        
        btn_frame = ctk.CTkFrame(parent)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="View Courses").pack(pady=5)
        ctk.CTkButton(btn_frame, text="My Progress").pack(pady=5)
        ctk.CTkButton(btn_frame, text="Assignments").pack(pady=5)
        
    def create_instructor_content(self, parent):
        info = ctk.CTkLabel(
            parent,
            text="Instructor Dashboard\n\nManage your courses and students.",
            font=("Arial", 14)
        )
        info.pack(pady=20)
        
        btn_frame = ctk.CTkFrame(parent)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="My Courses").pack(pady=5)
        ctk.CTkButton(btn_frame, text="Create Course").pack(pady=5)
        ctk.CTkButton(btn_frame, text="Student Analytics").pack(pady=5)
        
    def create_admin_content(self, parent):
        info = ctk.CTkLabel(
            parent,
            text="Admin Dashboard\n\nManage the entire platform.",
            font=("Arial", 14)
        )
        info.pack(pady=20)
        
        btn_frame = ctk.CTkFrame(parent)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Manage Users").pack(pady=5)
        ctk.CTkButton(btn_frame, text="Manage Courses").pack(pady=5)
        ctk.CTkButton(btn_frame, text="System Settings").pack(pady=5)
        ctk.CTkButton(btn_frame, text="Reports").pack(pady=5)
        
    def handle_logout(self):
        self.page_manager.set_user(None)
        self.page_manager.show_page("auth")