import customtkinter as ctk

class PageManager:
    """Manages different pages/frames in the application"""
    
    def __init__(self, master):
        self.master = master
        self.pages = {}
        self.current_page = None
        self.current_user = None  # Store logged-in user
        
    def add_page(self, name, page_class):
        """Add a page to the manager"""
        self.pages[name] = page_class
        
    def show_page(self, name, **kwargs):
        """Show a specific page by name"""
        # Hide current page if exists
        if self.current_page:
            self.current_page.pack_forget()
            
        # Create or get the page
        if name not in self.pages:
            raise ValueError(f"Page '{name}' not found")
            
        # Create new page instance
        page_class = self.pages[name]
        self.current_page = page_class(self.master, self, **kwargs)
        self.current_page.pack(fill="both", expand=True)
        
    def set_user(self, user):
        """Store the current logged-in user"""
        self.current_user = user
        
    def get_user(self):
        """Get the current logged-in user"""
        return self.current_user