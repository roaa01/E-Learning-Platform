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