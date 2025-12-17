"""
Admin Dashboard
Extracted from dashboard_page.py (admin content)
"""
import customtkinter as ctk


class AdminDashboard(ctk.CTkFrame):
    """Admin dashboard with management buttons"""
    
    def __init__(self, master, page_manager):
        super().__init__(master)
        self.page_manager = page_manager
        from database.admin_service import AdminService
        self.admin_service = AdminService()
        
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
            text="Role: Administrator",
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
            text="Admin Dashboard",
            font=("Arial", 20, "bold")
        )
        content_title.pack(pady=20)
        
        info = ctk.CTkLabel(
            content_frame,
            text="Manage the entire platform.",
            font=("Arial", 14)
        )
        info.pack(pady=10)
        
        # Management buttons
        btn_frame = ctk.CTkFrame(content_frame)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="Manage Users",
            command=self.manage_users
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Manage Courses",
            command=self.manage_courses
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
        
    def handle_logout(self):
        self.page_manager.set_user(None)
        self.page_manager.show_page("auth")

    def manage_users(self):
        """Open window to manage users"""
        win = ctk.CTkToplevel(self)
        win.title("Manage Users")
        win.geometry("600x500")
        
        ctk.CTkLabel(win, text="All Users", font=("Arial", 18, "bold")).pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        users = self.admin_service.get_all_users()
        for u in users:
            row = ctk.CTkFrame(scroll)
            row.pack(fill="x", pady=2)
            
            info = f"{u.get('name', 'N/A')} ({u.get('email', 'N/A')}) - {u.get('role', 'N/A')}"
            ctk.CTkLabel(row, text=info).pack(side="left", padx=5)
            
            # Prevent deleting self or critical logic could be added here
            uid = u.get("id") or str(u.get("_id"))
            
            ctk.CTkButton(
                row, 
                text="Delete", 
                fg_color="red", 
                width=60,
                command=lambda uid=uid, w=row: self.delete_user(uid, w)
            ).pack(side="right", padx=5)

    def delete_user(self, user_id, widget):
        if self.admin_service.delete_user(user_id):
            widget.destroy()
            print(f"Deleted user {user_id}")
            
    def manage_courses(self):
        """Open window to manage courses"""
        win = ctk.CTkToplevel(self)
        win.title("Manage Courses")
        win.geometry("600x500")
        
        ctk.CTkLabel(win, text="All Courses", font=("Arial", 18, "bold")).pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        courses = self.admin_service.get_all_courses()
        for c in courses:
            row = ctk.CTkFrame(scroll)
            row.pack(fill="x", pady=2)
            
            info = f"{c.get('title', 'Untitled')} - Status: {c.get('status', 'draft')}"
            ctk.CTkLabel(row, text=info).pack(side="left", padx=5)
            
            cid = c.get("id") or str(c.get("_id"))
            
            ctk.CTkButton(
                row, 
                text="Delete", 
                fg_color="red", 
                width=60,
                command=lambda cid=cid, w=row: self.delete_course(cid, w)
            ).pack(side="right", padx=5)

    def delete_course(self, course_id, widget):
        if self.admin_service.delete_course(course_id):
            widget.destroy()
            print(f"Deleted course {course_id}")
