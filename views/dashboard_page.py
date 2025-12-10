import customtkinter as ctk

class DashboardPage(ctk.CTkFrame):
    """Dashboard page shown after successful login/signup"""
    
    def __init__(self, master, page_manager):
        super().__init__(master)
        self.page_manager = page_manager

        
    def on_show(self):
        # Refresh dashboard content when shown
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()

        
    def create_widgets(self):
        user = self.page_manager.get_user()
        print("[DashboardPage] user:", user, "type:", type(user), "attrs:", dir(user))
        # Welcome Section
        welcome_frame = ctk.CTkFrame(self)
        welcome_frame.pack(pady=30, padx=30, fill="x")
        # Robust welcome label
        display_name = getattr(user, 'full_name', None) or getattr(user, 'username', None) or getattr(user, 'name', None) or str(user)
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text=f"Welcome, {display_name}!",
            font=("Arial", 28, "bold")
        )
        welcome_label.pack(pady=10)

        role = getattr(user, 'role', None)
        role_text = f"Role: {role.capitalize()}" if role else "Role: Unknown"
        role_label = ctk.CTkLabel(
            welcome_frame,
            text=role_text,
            font=("Arial", 16)
        )
        role_label.pack(pady=5)

        email = getattr(user, 'email', None)
        email_text = f"Email: {email}" if email else "Email: Unknown"
        email_label = ctk.CTkLabel(
            welcome_frame,
            text=email_text,
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
        
        ctk.CTkButton(btn_frame, text="View Courses", command=self.show_all_courses).pack(pady=5)
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
        
        ctk.CTkButton(btn_frame, text="My Courses", command=self.show_my_courses).pack(pady=5)
        ctk.CTkButton(btn_frame, text="Create Course", command=lambda: self.page_manager.show_page("create_course")).pack(pady=5)
        ctk.CTkButton(btn_frame, text="Student Analytics").pack(pady=5)
        ctk.CTkButton(btn_frame, text="Student Analytics").pack(pady=5)
        ctk.CTkButton(btn_frame, text="View All Courses", command=self.show_all_courses).pack(pady=5)

    def show_all_courses(self):
        courses_page = self.page_manager.get_page("courses")
        courses_page.set_mode("all")
        self.page_manager.show_page("courses")

    def show_my_courses(self):
        user = self.page_manager.get_user()
        if user:
            # Robust ID extraction: user.id might be None, so check it first
            uid = getattr(user, 'id', None)
            if not uid:
                uid = getattr(user, '_id', None)
            uid = str(uid) if uid else ""
            
            print(f"[Dashboard] Filtering courses for instructor_id: {uid}")
            courses_page = self.page_manager.get_page("courses")
            # Set mode to instructor so it fetches courses by this instructor ID
            courses_page.set_mode("instructor", uid)
            self.page_manager.show_page("courses")

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