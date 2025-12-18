import customtkinter as ctk
from database.course_service import CourseService


class ManageResourcesPage(ctk.CTkFrame):
    """Page for instructors to upload resources (videos, PDFs, links) to lessons"""
    
    def __init__(self, master, page_manager):
        super().__init__(master)
        self.page_manager = page_manager
        self.course_service = CourseService()
        self.course_id = None
        self.module_id = None
        self.lesson_id = None
        
        self.create_widgets()
        
    def set_context(self, course_id, module_id, lesson_id):
        """Set the context for resource upload"""
        self.course_id = course_id
        self.module_id = module_id
        self.lesson_id = lesson_id
        self.refresh_display()
    
    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(pady=20, padx=30, fill="x")
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Manage Resources",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(side="left")
        
        back_btn = ctk.CTkButton(
            header_frame,
            text="Back",
            command=self.go_back,
            width=80
        )
        back_btn.pack(side="right")
        
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        # Resources list
        resources_label = ctk.CTkLabel(main_frame, text="Lesson Resources", font=("Arial", 14, "bold"))
        resources_label.pack(anchor="w", pady=(0, 10))
        
        self.resources_frame = ctk.CTkScrollableFrame(main_frame)
        self.resources_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Add resource form
        form_label = ctk.CTkLabel(main_frame, text="Add New Resource", font=("Arial", 12, "bold"))
        form_label.pack(anchor="w", pady=(20, 10))
        
        form_frame = ctk.CTkFrame(main_frame, fg_color="gray20")
        form_frame.pack(fill="x")
        
        # Resource type
        type_label = ctk.CTkLabel(form_frame, text="Type:", font=("Arial", 11))
        type_label.pack(anchor="w", padx=15, pady=(15, 5))
        self.type_combo = ctk.CTkComboBox(
            form_frame,
            values=["video", "pdf", "link", "document"],
            state="readonly"
        )
        self.type_combo.set("video")
        self.type_combo.pack(fill="x", padx=15, pady=5)
        
        # Resource name/title
        name_label = ctk.CTkLabel(form_frame, text="Resource Name:", font=("Arial", 11))
        name_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., Introduction Video")
        self.name_entry.pack(fill="x", padx=15, pady=5)
        
        # URL/Path
        url_label = ctk.CTkLabel(form_frame, text="URL or File Path:", font=("Arial", 11))
        url_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.url_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., https://example.com/video.mp4")
        self.url_entry.pack(fill="x", padx=15, pady=5)
        
        # Description
        desc_label = ctk.CTkLabel(form_frame, text="Description (optional):", font=("Arial", 11))
        desc_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.desc_entry = ctk.CTkTextbox(form_frame, height=60)
        self.desc_entry.pack(fill="x", padx=15, pady=5)
        
        # Add button
        add_btn = ctk.CTkButton(
            form_frame,
            text="+ Add Resource",
            command=self.handle_add_resource,
            fg_color="green",
            hover_color="darkgreen",
            height=35
        )
        add_btn.pack(fill="x", padx=15, pady=15)
        
        # Message label
        self.message_label = ctk.CTkLabel(self, text="", font=("Arial", 11), text_color="gray")
        self.message_label.pack(pady=10)
    
    def refresh_display(self):
        """Refresh the resources list"""
        if not self.course_id or not self.module_id or not self.lesson_id:
            return
        
        course = self.course_service.get_course(self.course_id)
        if not course:
            return
        
        # Find the lesson
        lesson = None
        for module in course.get("modules", []):
            if module.get("id") == self.module_id:
                for l in module.get("lessons", []):
                    if l.get("id") == self.lesson_id:
                        lesson = l
                        break
        
        # Update title
        lesson_title = lesson.get("title", "Lesson") if lesson else "Lesson"
        self.title_label.configure(text=f"Resources: {lesson_title}")
        
        # Clear resources frame
        for widget in self.resources_frame.winfo_children():
            widget.destroy()
        
        # Display resources
        if not lesson or not lesson.get("resources"):
            no_resources = ctk.CTkLabel(
                self.resources_frame,
                text="No resources yet",
                text_color="gray"
            )
            no_resources.pack(pady=20)
        else:
            for i, resource in enumerate(lesson.get("resources", [])):
                self.create_resource_item(i, resource)
    
    def create_resource_item(self, index, resource):
        """Create a resource item display"""
        item = ctk.CTkFrame(self.resources_frame, fg_color="gray19")
        item.pack(fill="x", pady=5, padx=0)
        
        # Resource info
        info_frame = ctk.CTkFrame(item, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=8, anchor="w")
        
        # Type badge
        resource_type = resource.get("type", "unknown").upper()
        type_colors = {
            "VIDEO": "lightblue",
            "PDF": "lightyellow",
            "LINK": "lightgreen",
            "DOCUMENT": "lightcyan"
        }
        type_color = type_colors.get(resource_type, "gray")
        
        type_label = ctk.CTkLabel(
            info_frame,
            text=f"[{resource_type}]",
            font=("Arial", 10, "bold"),
            text_color=type_color
        )
        type_label.pack(side="left", padx=5)
        
        # Name
        name = ctk.CTkLabel(
            info_frame,
            text=resource.get("name", "Untitled"),
            font=("Arial", 11, "bold")
        )
        name.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            item,
            text="Remove",
            command=lambda: self.delete_resource(index),
            width=60,
            height=25,
            fg_color="red",
            hover_color="darkred",
            font=("Arial", 9)
        )
        delete_btn.pack(side="right", padx=10, pady=5)
        
        # URL (if it's a link or has URL)
        if resource.get("url"):
            url_label = ctk.CTkLabel(
                info_frame,
                text=f"URL: {resource.get('url', 'N/A')}",
                font=("Arial", 9),
                text_color="gray",
                wraplength=300
            )
            url_label.pack(anchor="w", padx=5, pady=3)
    
    def handle_add_resource(self):
        """Add a new resource to the lesson"""
        resource_type = self.type_combo.get()
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        description = self.desc_entry.get("1.0", "end").strip()
        
        # Validation
        if not name:
            self.show_message("Please enter a resource name", "red")
            return
        
        if not url:
            self.show_message("Please enter a URL or file path", "red")
            return
        
        try:
            # Build resource object
            resource = {
                "type": resource_type,
                "name": name,
                "url": url,
                "description": description if description else None,
                "uploadedAt": None  # Can add timestamp if needed
            }
            
            # Upload resource
            success = self.course_service.upload_resource(
                self.course_id,
                self.module_id,
                self.lesson_id,
                resource
            )
            
            if success:
                self.show_message(f"Resource '{name}' added successfully!", "green")
                self.clear_form()
                self.refresh_display()
            else:
                self.show_message("Failed to add resource", "red")
        
        except Exception as e:
            self.show_message(f"Error: {str(e)}", "red")
            print(f"Resource upload error: {e}")
    
    def delete_resource(self, index):
        """Delete a resource"""
        if not self.course_id or not self.module_id or not self.lesson_id:
            return

        try:
            success = self.course_service.delete_resource(
                self.course_id, 
                self.module_id, 
                self.lesson_id, 
                index
            )
            
            if success:
                self.show_message("Resource deleted successfully", "green")
                self.refresh_display()
            else:
                self.show_message("Failed to delete resource", "red")
                
        except Exception as e:
            self.show_message(f"Error deleting resource: {str(e)}", "red")
            print(f"Delete resource error: {e}")
    
    def clear_form(self):
        """Clear the form fields"""
        self.type_combo.set("video")
        self.name_entry.delete(0, "end")
        self.url_entry.delete(0, "end")
        self.desc_entry.delete("1.0", "end")
    
    def show_message(self, message: str, color: str):
        """Display a message"""
        self.message_label.configure(text=message, text_color=color)
    
    def go_back(self):
        """Go back to manage course page"""
        self.page_manager.show_page("manage_course")
