import customtkinter as ctk
from database.course_service import CourseService
from database.EnrollmentService import EnrollmentService
from database.seed import get_database

class ManageCoursePage(ctk.CTkFrame):
    """Page for instructors to manage course modules and lessons"""
    
    def __init__(self, master, page_manager):
        super().__init__(master)
        self.page_manager = page_manager
        self.course_service = CourseService()
        
        db = get_database()
        self.enrollment_service = EnrollmentService(
            db.get_collection("enrollments"),
            db.get_collection("courses")
        )
        
        self.course_id = None
        self.course_data = None
        self.status_btn = None
        
        self.create_widgets()
        
    def set_course(self, course_id):
        """Set the course to manage"""
        self.course_id = course_id
        self.course_data = self.course_service.get_course(course_id)
        self.update_status_ui()
        self.refresh_display()
    
    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(pady=20, padx=30, fill="x")
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Manage Course",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(side="left")
        
        # Status toggle (will be enabled for instructors/admins)
        self.status_btn = ctk.CTkButton(
            header_frame,
            text="Status: -",
            command=self.toggle_visibility,
            width=140,
            fg_color="gray",
            hover_color="gray"
        )
        self.status_btn.pack(side="right", padx=(6, 0))
        
        # View Enrollments Button
        self.enrollments_btn = ctk.CTkButton(
            header_frame,
            text="Enrollments",
            command=self.show_enrollments_dialog,
            width=100,
            fg_color="purple",
            hover_color="darkviolet"
        )
        self.enrollments_btn.pack(side="right", padx=(6, 0))
        
        back_btn = ctk.CTkButton(
            header_frame,
            text="Back",
            command=self.go_back,
            width=80
        )
        back_btn.pack(side="right")
        
        # Main container with two sections
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        # Left side: Modules list
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        modules_label = ctk.CTkLabel(left_frame, text="Modules", font=("Arial", 14, "bold"))
        modules_label.pack(anchor="w", pady=(0, 10))
        
        self.modules_frame = ctk.CTkScrollableFrame(left_frame)
        self.modules_frame.pack(fill="both", expand=True)
        
        # Add module button
        add_module_btn = ctk.CTkButton(
            left_frame,
            text="+ Add Module",
            command=self.show_add_module_dialog,
            fg_color="green",
            hover_color="darkgreen",
            height=30
        )
        add_module_btn.pack(fill="x", pady=(10, 0))
        
        # Right side: Module details and lessons
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        details_label = ctk.CTkLabel(right_frame, text="Module Details", font=("Arial", 14, "bold"))
        details_label.pack(anchor="w", pady=(0, 10))
        
        self.details_frame = ctk.CTkScrollableFrame(right_frame)
        self.details_frame.pack(fill="both", expand=True)
        
        # Add lesson button
        add_lesson_btn = ctk.CTkButton(
            right_frame,
            text="+ Add Lesson",
            command=self.show_add_lesson_dialog,
            fg_color="blue",
            hover_color="darkblue",
            height=30
        )
        add_lesson_btn.pack(fill="x", pady=(10, 0))
           # Bottom section with Done button centered
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(pady=20, fill="x")
        
        done_btn = ctk.CTkButton(
            bottom_frame,
            text="Done",
            command=self.go_back,
            width=120,
            height=35,
            fg_color="blue",
            hover_color="darkblue"
        )
        done_btn.pack()
        self.message_label = ctk.CTkLabel(self, text="", font=("Arial", 11), text_color="gray")
        self.message_label.pack(pady=10)

    def refresh_display(self):
        """Refresh the modules and details display"""
        if not self.course_data:
            return
        # keep status UI in sync
        self.update_status_ui()
        
        # Update title
        self.title_label.configure(text=f"Manage: {self.course_data.get('title', 'Course')}")
        
        # Clear modules frame
        for widget in self.modules_frame.winfo_children():
            widget.destroy()
        
        # Clear details frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Display modules
        modules = self.course_data.get("modules", [])
        if not modules:
            no_modules_label = ctk.CTkLabel(
                self.modules_frame,
                text="No modules yet",
                text_color="gray"
            )
            no_modules_label.pack(pady=20)
        else:
            for i, module in enumerate(modules):
                self.create_module_item(i, module)
        
        # Display details of first module if exists
        if modules:
            self.display_module_details(0, modules[0])
    
    def create_module_item(self, index, module):
        """Create a clickable module item"""
        item = ctk.CTkFrame(self.modules_frame, fg_color="gray20")
        item.pack(fill="x", pady=5, padx=0)
        
        title = ctk.CTkLabel(
            item,
            text=f"{module.get('title', 'Module')}",
            font=("Arial", 12, "bold"),
            text_color="lightblue"
        )
        title.pack(side="left", padx=10, pady=8)
        
        lessons_count = len(module.get("lessons", []))
        count = ctk.CTkLabel(
            item,
            text=f"({lessons_count} lessons)",
            font=("Arial", 10),
            text_color="gray"
        )
        count.pack(side="left", padx=5, pady=8)
        
        delete_btn = ctk.CTkButton(
            item,
            text="Delete",
            command=lambda: self.delete_module(index),
            width=60,
            height=25,
            fg_color="red",
            hover_color="darkred",
            font=("Arial", 9)
        )
        delete_btn.pack(side="right", padx=5, pady=5)
        
        # Make item clickable to show details
        item.bind("<Button-1>", lambda e: self.display_module_details(index, module))
        title.bind("<Button-1>", lambda e: self.display_module_details(index, module))
    
    def display_module_details(self, index, module):
        """Display lessons of a selected module"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        module_title = ctk.CTkLabel(
            self.details_frame,
            text=f"{module.get('title', 'Module')} - Lessons",
            font=("Arial", 13, "bold")
        )
        module_title.pack(anchor="w", pady=(0, 10))
        
        lessons = module.get("lessons", [])
        if not lessons:
            no_lessons = ctk.CTkLabel(
                self.details_frame,
                text="No lessons yet",
                text_color="gray"
            )
            no_lessons.pack(pady=20)
        else:
            for j, lesson in enumerate(lessons):
                self.create_lesson_item(index, j, lesson)
        
        # Store current module index for adding lessons
        self.current_module_index = index
    
    def create_lesson_item(self, module_index, lesson_index, lesson):
        """Create a lesson item display"""
        item = ctk.CTkFrame(self.details_frame, fg_color="gray19")
        item.pack(fill="x", pady=5, padx=0)
        
        info_frame = ctk.CTkFrame(item, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=8, anchor="w")
        
        title = ctk.CTkLabel(
            info_frame,
            text=f"• {lesson.get('title', 'Lesson')}",
            font=("Arial", 11, "bold")
        )
        title.pack(anchor="w", pady=(0, 3))
        
        lesson_type = ctk.CTkLabel(
            info_frame,
            text=f"Type: {lesson.get('type', 'unknown')}",
            font=("Arial", 10),
            text_color="lightgreen"
        )
        lesson_type.pack(anchor="w", pady=2)
        
        # Button frame for actions
        btn_frame = ctk.CTkFrame(item, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=5)
        
        # Manage resources button
        resources_btn = ctk.CTkButton(
            btn_frame,
            text="Resources",
            command=lambda: self.manage_lesson_resources(module_index, lesson_index, lesson),
            width=75,
            height=25,
            fg_color="purple",
            hover_color="darkviolet",
            font=("Arial", 9)
        )
        resources_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Remove",
            command=lambda: self.delete_lesson(module_index, lesson_index),
            width=60,
            height=25,
            fg_color="red",
            hover_color="darkred",
            font=("Arial", 9)
        )
        delete_btn.pack(side="left", padx=5)

    def update_status_ui(self):
        """Update status button text and enabled state based on current course and user role"""
        if not self.course_data:
            self.status_btn.configure(text="Status: -", fg_color="gray", hover_color="gray")
            try:
                self.status_btn.configure(state="disabled")
            except Exception:
                pass
            return

        status = self.course_data.get("status", "draft")
        # Determine if current user can change visibility
        user = self.page_manager.get_user()
        can_manage = False
        try:
            if user:
                role = getattr(user, 'role', None)
                uid = str(getattr(user, 'id', getattr(user, '_id', None)))
                if role == 'admin' or (role == 'instructor' and uid and uid == str(self.course_data.get('instructorId'))):
                    can_manage = True
        except Exception:
            can_manage = False

        label = f"Status: {status.capitalize()}"
        # Update appearance
        if status == 'published':
            self.status_btn.configure(text=label, fg_color="green", hover_color="darkgreen")
        else:
            self.status_btn.configure(text=label, fg_color="orange", hover_color="darkorange")

        try:
            if can_manage:
                self.status_btn.configure(state="normal")
            else:
                self.status_btn.configure(state="disabled")
        except Exception:
            pass

    def toggle_visibility(self):
        """Toggle course visibility between published and draft"""
        if not self.course_id:
            return
        current = self.course_data.get('status', 'draft') if self.course_data else 'draft'
        new_status = 'draft' if current == 'published' else 'published'
        try:
            ok = self.course_service.set_visibility(self.course_id, new_status)
            if ok:
                # refresh local course data and UI
                self.course_data = self.course_service.get_course(self.course_id)
                self.update_status_ui()
                self.show_message(f"Status set to {new_status}", "green")
            else:
                self.show_message("Failed to change status", "red")
        except Exception as e:
            self.show_message(f"Error: {e}", "red")
    
    def show_add_module_dialog(self):
        """Show dialog to add a new module"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Module")
        dialog.geometry("400x150")
        
        label = ctk.CTkLabel(dialog, text="Module Title:", font=("Arial", 12, "bold"))
        label.pack(pady=(20, 5), padx=20)
        
        entry = ctk.CTkEntry(dialog, placeholder_text="Enter module title")
        entry.pack(pady=5, padx=20, fill="x")
        
        def add():
            title = entry.get().strip()
            if not title:
                return
            self.add_module(title)
            dialog.destroy()
        
        btn = ctk.CTkButton(dialog, text="Add", command=add, fg_color="green")
        btn.pack(pady=20)
    
    def show_add_lesson_dialog(self):
        """Show dialog to add a new lesson"""
        if not hasattr(self, 'current_module_index'):
            self.show_message("Select a module first", "red")
            return
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Lesson")
        dialog.geometry("400x400")
        
        # Lesson title
        ctk.CTkLabel(dialog, text="Lesson Title:", font=("Arial", 11, "bold")).pack(pady=(15, 3), padx=20)
        title_entry = ctk.CTkEntry(dialog, placeholder_text="Enter lesson title")
        title_entry.pack(pady=5, padx=20, fill="x")
        
        # Lesson content
        ctk.CTkLabel(dialog, text="Content:", font=("Arial", 11, "bold")).pack(pady=(10, 3), padx=20)
        content_entry = ctk.CTkTextbox(dialog, height=100)
        content_entry.pack(pady=5, padx=20, fill="both", expand=True)
        
        # Lesson type
        ctk.CTkLabel(dialog, text="Type:", font=("Arial", 11, "bold")).pack(pady=(10, 3), padx=20)
        type_combo = ctk.CTkComboBox(
            dialog,
            values=["video", "text", "quiz", "assignment"],
            state="readonly"
        )
        type_combo.set("video")
        type_combo.pack(pady=5, padx=20, fill="x")
        
        def add():
            title = title_entry.get().strip()
            content = content_entry.get("1.0", "end").strip()
            lesson_type = type_combo.get()
            
            if not title or not content:
                return
            
            self.add_lesson(title, content, lesson_type)
            dialog.destroy()
        
        btn = ctk.CTkButton(dialog, text="Add Lesson", command=add, fg_color="blue")
        btn.pack(pady=15, padx=20, fill="x")
    
    def add_module(self, title):
        """Add a new module to the course"""
        try:
            module_id = self.course_service.add_module(self.course_id, title)
            if module_id:
                self.course_data = self.course_service.get_course(self.course_id)
                self.refresh_display()
                self.show_message(f"Module '{title}' added", "green")
            else:
                self.show_message("Failed to add module", "red")
        except Exception as e:
            self.show_message(f"Error: {str(e)}", "red")
    
    def add_lesson(self, title, content, lesson_type):
        """Add a new lesson to the current module"""
        try:
            module_id = self.course_data.get("modules", [])[self.current_module_index].get("id")
            lesson_id = self.course_service.add_lesson(self.course_id, module_id, title, content, lesson_type)
            if lesson_id:
                self.course_data = self.course_service.get_course(self.course_id)
                self.refresh_display()
                self.show_message(f"Lesson '{title}' added", "green")
            else:
                self.show_message("Failed to add lesson", "red")
        except Exception as e:
            self.show_message(f"Error: {str(e)}", "red")
    
    def delete_module(self, index):
        """Delete a module"""
        modules = self.course_data.get("modules", [])
        if index >= len(modules):
            return
            
        module_id = modules[index].get("id")
        
        # Confirm dialog could be added here, but for now direct delete
        success = self.course_service.delete_module(self.course_id, module_id)
        if success:
            self.course_data = self.course_service.get_course(self.course_id)
            self.refresh_display()
            self.show_message("Module deleted successfully", "green")
        else:
            self.show_message("Failed to delete module", "red")
    
    def manage_lesson_resources(self, module_index, lesson_index, lesson):
        """Navigate to manage resources page"""
        module_id = self.course_data.get("modules", [])[module_index].get("id")
        lesson_id = lesson.get("id")
        
        resources_page = self.page_manager.get_page("manage_resources")
        resources_page.set_context(self.course_id, module_id, lesson_id)
        self.page_manager.show_page("manage_resources")
    
    def delete_lesson(self, module_index, lesson_index):
        """Delete a lesson"""
        modules = self.course_data.get("modules", [])
        if module_index >= len(modules):
            return
            
        module = modules[module_index]
        lessons = module.get("lessons", [])
        if lesson_index >= len(lessons):
            return
            
        lesson_id = lessons[lesson_index].get("id")
        module_id = module.get("id")
        
        success = self.course_service.delete_lesson(self.course_id, module_id, lesson_id)
        if success:
            self.course_data = self.course_service.get_course(self.course_id)
            self.refresh_display()
            # If we just deleted the last lesson, display might need adjustment, but refresh handles it
            self.show_message("Lesson deleted successfully", "green")
        else:
            self.show_message("Failed to delete lesson", "red")
    
    def show_message(self, message: str, color: str):
        """Display a message"""
        self.message_label.configure(text=message, text_color=color)
    
    def go_back(self):
        """Go back to dashboard"""
        self.page_manager.show_page("dashboard")

    def show_enrollments_dialog(self):
        """Show pending enrollments for this course"""
        if not self.course_id:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Enrollment Requests - {self.course_data.get('title')}")
        dialog.geometry("500x400")
        
        # Header
        ctk.CTkLabel(dialog, text="Pending Requests", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Requests list
        scroll = ctk.CTkScrollableFrame(dialog)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        requests = self.enrollment_service.get_pending_enrollments(self.course_id)
        
        if not requests:
            ctk.CTkLabel(scroll, text="No pending requests", text_color="gray").pack(pady=20)
        else:
            for req in requests:
                req_frame = ctk.CTkFrame(scroll, fg_color="gray20")
                req_frame.pack(fill="x", pady=5)
                
                # Student Info
                info = ctk.CTkFrame(req_frame, fg_color="transparent")
                info.pack(side="left", padx=10, pady=10)
                
                ctk.CTkLabel(info, text=req.get("student_name", "Unknown"), font=("Arial", 12, "bold")).pack(anchor="w")
                ctk.CTkLabel(info, text=req.get("student_email", ""), font=("Arial", 10)).pack(anchor="w")
                
                # Approve Button
                def approve(eid=req.get("enrollment_id")):
                    if self.enrollment_service.approve_enrollment(eid):
                        req_frame.destroy()
                        # Refresh list to see if empty
                        if not scroll.winfo_children():
                             ctk.CTkLabel(scroll, text="No pending requests", text_color="gray").pack(pady=20)
                        self.show_message("Enrollment approved", "green")
                    else:
                        self.show_message("Failed to approve", "red")
                        
                ctk.CTkButton(req_frame, text="Approve", command=approve, fg_color="green", width=80).pack(side="right", padx=10)
