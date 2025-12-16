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
            text="Manage Users"
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Manage Courses"
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="System Settings"
        ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Reports"
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
