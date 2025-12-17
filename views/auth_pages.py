"""
Authentication pages: AuthPage, LoginPage, SignupPage
Consolidated from auth_page.py, login.py, signup.py
"""
import customtkinter as ctk


class AuthPage(ctk.CTkFrame):
    """Authentication page with sign up and login functionality"""
    
    def __init__(self, master, page_manager, service):
        super().__init__(master)
        self.page_manager = page_manager
        self.service = service
        
        self.create_widgets()
        
    def create_widgets(self):
        title_label = ctk.CTkLabel(
            self, text="User Authentication", font=("Arial", 22, "bold")
        )
        title_label.pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        
        signup_btn = ctk.CTkButton(
            button_frame, 
            text="Sign Up", 
            command=lambda: self.switch_option("signup"),
            width=150,
            height=40
        )
        signup_btn.grid(row=0, column=0, padx=10, pady=10)
        
        login_btn = ctk.CTkButton(
            button_frame, 
            text="Log In", 
            command=lambda: self.switch_option("login"),
            width=150,
            height=40
        )
        login_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Message Label
        self.msg_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.msg_label.pack(pady=10)
    
    def switch_option(self, switch_to):
        print(f"Switching to {switch_to}")  # Debug print
        
        if switch_to == "login":
            self.page_manager.show_page("login")
        else:
            self.page_manager.show_page("signup")


class LoginPage(ctk.CTkFrame):
    """Login page for existing users"""
    
    def __init__(self, master, page_manager, service):
        super().__init__(master)
        self.page_manager = page_manager
        self.service = service
        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(
            self, text="Login", font=("Arial", 22, "bold")
        )
        title_label.pack(pady=20)
        
        # Email/Username
        email_label = ctk.CTkLabel(self, text="Email")
        email_label.pack()
        
        self.email_entry = ctk.CTkEntry(self, width=250)
        self.email_entry.pack(pady=5)
        
        # Password
        password_label = ctk.CTkLabel(self, text="Password")
        password_label.pack()
        
        self.password_entry = ctk.CTkEntry(self, show="*", width=250)
        self.password_entry.pack(pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        
        login_btn = ctk.CTkButton(
            button_frame, text="Log In", command=self.handle_login
        )
        login_btn.grid(row=0, column=0, padx=10)
        
        back_btn = ctk.CTkButton(
            button_frame, 
            text="Back", 
            command=lambda: self.page_manager.show_page("auth"),
            fg_color="gray",
            hover_color="darkgray"
        )
        back_btn.grid(row=0, column=1, padx=10)
        
        # Message Label
        self.msg_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.msg_label.pack(pady=10)

    def handle_login(self):
        email_or_username = self.email_entry.get()
        password = self.password_entry.get()
        
        # Validate inputs
        if not email_or_username or not password:
            self.msg_label.configure(
                text="Please enter email/username and password", text_color="red"
            )
            return
        
        user = self.service.log_in(email_or_username, password)
        print("Trying to login:", email_or_username, password)
        
        if user:
            self.msg_label.configure(
                text=f"Logged in: {getattr(user, 'username', email_or_username)}", 
                text_color="green"
            )
            self.page_manager.set_user(user)
            self.page_manager.show_page("dashboard")
        else:
            self.msg_label.configure(text="Login failed", text_color="red")


class SignupPage(ctk.CTkFrame):
    """Signup page for new users"""
    
    def __init__(self, master, page_manager, service):
        super().__init__(master)
        self.page_manager = page_manager
        self.service = service
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(
            self, text="Sign Up", font=("Arial", 22, "bold")
        )
        title_label.pack(pady=20)
        
        # Role Dropdown
        role_label = ctk.CTkLabel(self, text="Role")
        role_label.pack()
        
        self.role_option = ctk.CTkComboBox(
            self, values=["Student", "Instructor"],
        )
        self.role_option.pack(pady=5)
        
        # Name
        name_label = ctk.CTkLabel(self, text="Name")
        name_label.pack()
        
        self.name_entry = ctk.CTkEntry(self, width=250)
        self.name_entry.pack(pady=5)
        
        # Email
        email_label = ctk.CTkLabel(self, text="Email")
        email_label.pack()
        
        self.email_entry = ctk.CTkEntry(self, width=250)
        self.email_entry.pack(pady=5)
        
        # Password
        password_label = ctk.CTkLabel(self, text="Password")
        password_label.pack()
        
        self.password_entry = ctk.CTkEntry(self, show="*", width=250)
        self.password_entry.pack(pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        
        signup_btn = ctk.CTkButton(
            button_frame, text="Sign Up", command=self.handle_signup
        )
        signup_btn.grid(row=0, column=0, padx=10)
        
        back_btn = ctk.CTkButton(
            button_frame, 
            text="Back", 
            command=lambda: self.page_manager.show_page("auth"),
            fg_color="gray",
            hover_color="darkgray"
        )
        back_btn.grid(row=0, column=1, padx=10)
        
        # Message Label
        self.msg_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.msg_label.pack(pady=10)
        
    def handle_signup(self):
        # Normalize role
        raw_role = self.role_option.get()
        role = (raw_role or "").strip().lower()
        if role == "":
            role = "student"
        
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        # Validate inputs
        if not name or not email or not password:
            self.msg_label.configure(
                text="Please fill all fields", text_color="red"
            )
            return
        
        # Pass correct arguments to sign_up (username and full_name)
        user = self.service.sign_up(role, name, email, password)
        
        if user:
            self.msg_label.configure(
                text=f"Sign up success: {getattr(user, 'username', name)}", 
                text_color="green"
            )
            # Store user and navigate to dashboard
            self.page_manager.set_user(user)
            self.page_manager.show_page("dashboard")
        else:
            self.msg_label.configure(text="Sign up failed", text_color="red")
