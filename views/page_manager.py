import customtkinter as ctk

class PageManager:
    
    def __init__(self, master):
        self.master = master
        self.pages = {}
        self.page_instances = {}  
        self.current_page = None
        self.current_user = None  # Store logged-in user
        
    def add_page(self, name, page_class):
        """Add a page to the manager (instantiate once and reuse)"""
        self.pages[name] = page_class(self.master, self)

    def get_page(self, name):
        """Get or create a page instance"""
        if name not in self.page_instances:
            page_class = self.pages[name]
            self.page_instances[name] = page_class(self.master, self)
        return self.page_instances[name]
    def show_page(self, name, **kwargs):
        """Show a specific page by name (reuse instance)"""
        
        # Hide current page
        if self.current_page:
            self.current_page.pack_forget()
        
        # Validate page
        if name not in self.pages:
            raise ValueError(f"Page '{name}' not found")
        
        self.current_page = self.pages[name]

    
        if hasattr(self.current_page, "on_show"):
            self.current_page.on_show()
        
        # Show new page
        self.current_page = self.get_page(name)
        self.current_page.pack(fill="both", expand=True)
        
    def set_user(self, user):
        """Store the current logged-in user"""
        self.current_user = user
        
    def get_user(self):
        """Get the current logged-in user"""
        return self.current_user
