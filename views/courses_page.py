import customtkinter as ctk
from database.course_service import CourseService
from database.EnrollmentService import EnrollmentService
from models.user import Student
from database.seed import get_database

class CoursesPage(ctk.CTkFrame):
    """Page to display all available courses"""
    
    def __init__(self, master, page_manager):
        super().__init__(master)
        self.page_manager = page_manager
        self.course_service = CourseService()
        # Add EnrollmentService initialization
        db = get_database()
        self.enrollment_service = EnrollmentService(
            db.get_collection("enrollments"),
            db.get_collection("courses")
        )
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(pady=15, padx=20, fill="x")
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Available Courses",
            font=("Arial", 20, "bold")
        )
        self.title_label.pack(side="left")
        
        back_btn = ctk.CTkButton(
            header_frame,
            text="Back",
            command=self.go_back,
            width=80
        )
        back_btn.pack(side="right")
        
        # Scrollable courses container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.filter_mode = "all"  # or "instructor"
        self.filter_id = None

    def set_mode(self, mode="all", filter_id=None):
        self.filter_mode = mode
        self.filter_id = filter_id
        self.refresh_courses()

    def send_enrollment_request(self, student, course_id):
        """Call EnrollmentService to send an enrollment request for a student and provide feedback."""
        success = self.enrollment_service.enroll_student(student, course_id)
        return success

    def create_course_card(self, parent, course):
        """Create a card widget for a single course"""
        card = ctk.CTkFrame(parent, fg_color="gray20")
        card.pack(pady=8, padx=0, fill="x")
        
        # Course Title
        title = ctk.CTkLabel(
            card,
            text=course.get("title", "Untitled Course"),
            font=("Arial", 14, "bold")
        )
        title.pack(pady=(8, 3), padx=12, anchor="w")
        
        # Course Description
        desc = ctk.CTkLabel(
            card,
            text=course.get("description", "No description"),
            font=("Arial", 10),
            text_color="gray",
            wraplength=400
        )
        desc.pack(pady=3, padx=12, anchor="w")
        
        # Course Info (Category, Modules count)
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(pady=3, padx=12, fill="x")
        
        category = ctk.CTkLabel(
            info_frame,
            text=f"Category: {course.get('category', 'N/A')}",
            font=("Arial", 10),
            text_color="lightblue"
        )
        category.pack(side="left", padx=5)
        
        modules_count = len(course.get("modules", []))
        modules_label = ctk.CTkLabel(
            info_frame,
            text=f"Modules: {modules_count}",
            font=("Arial", 10),
            text_color="lightgreen"
        )
        modules_label.pack(side="left", padx=5)
        
        # Action buttons frame
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=(3, 8))

        # Enroll button for students
        user = self.page_manager.get_user()
        if user and getattr(user, 'role', None) == 'student':
            enroll_btn = ctk.CTkButton(actions, text="Request Enrollment", command=lambda: self.handle_enroll(user, course.get("id"), actions), width=150, height=28)
            enroll_btn.pack(side="right", padx=5)

        # Show edit/delete only for admin or course instructor
        user = self.page_manager.get_user()
        show_manage = False
        try:
            if user:
                role = getattr(user, "role", None)
                # Robust ID extraction
                uid = getattr(user, 'id', None)
                if not uid:
                    uid = getattr(user, '_id', None)
                uid = str(uid) if uid else ""

                if role == "admin":
                    show_manage = True
                if role == "instructor" and uid and uid == str(course.get("instructorId")):
                    show_manage = True
        except Exception as e:
            print(f"Error checking manage permissions: {e}")
            show_manage = False

        if show_manage:
            edit_btn = ctk.CTkButton(actions, text="Edit", command=lambda: self.show_edit_dialog(course), width=80, height=28)
            edit_btn.pack(side="right", padx=5)

            del_btn = ctk.CTkButton(actions, text="Delete", fg_color="red", hover_color="darkred",
                                    command=lambda: self.confirm_delete(course.get("id")), width=80, height=28)
            del_btn.pack(side="right", padx=5)
    
    def handle_enroll(self, user, course_id, parent_widget):
        """Handle enrollment request and show feedback in the course card."""
        success = self.send_enrollment_request(user, course_id)
        for widget in parent_widget.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text").startswith("Enrollment"):  # Remove old feedback
                widget.destroy()
        if success:
            feedback = ctk.CTkLabel(parent_widget, text="Enrollment request sent!", text_color="green")
        else:
            feedback = ctk.CTkLabel(parent_widget, text="Already requested or enrolled.", text_color="orange")
        feedback.pack(side="left", padx=6)

    def view_course_details(self, course_id):
        """Show a dialog with course details: modules, lessons, resources."""
        course = self.course_service.get_course(course_id)
        if not course:
            dlg = ctk.CTkToplevel(self)
            dlg.title("Course Not Found")
            ctk.CTkLabel(dlg, text="Course not found or has been removed.").pack(padx=20, pady=20)
            return
        user = self.page_manager.get_user()
        dlg = ctk.CTkToplevel(self)
        dlg.title(course.get("title", "Course Details"))
        dlg.geometry("700x600")

        header = ctk.CTkFrame(dlg)
        header.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(header, text=course.get("title", ""), font=("Arial", 18, "bold")).pack(anchor="w")
        ctk.CTkLabel(header, text=f"Category: {course.get('category','N/A')}   |   Status: {course.get('status','')}", text_color="gray").pack(anchor="w")

        body = ctk.CTkScrollableFrame(dlg)
        body.pack(fill="both", expand=True, padx=12, pady=(0,12))

        # Description
        ctk.CTkLabel(body, text="Description:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(6,2))
        ctk.CTkLabel(body, text=course.get("description", ""), wraplength=640, text_color="gray").pack(anchor="w", pady=(0,8))

        # Modules and lessons
        modules = course.get("modules", [])
        if not modules:
            ctk.CTkLabel(body, text="No modules yet", text_color="gray").pack(pady=10)
        else:
            for m in modules:
                m_frame = ctk.CTkFrame(body, fg_color="gray20")
                m_frame.pack(fill="x", pady=6)
                ctk.CTkLabel(m_frame, text=m.get("title","Module"), font=("Arial", 12, "bold")).pack(anchor="w", padx=8, pady=(6,2))
                for l in m.get("lessons", []):
                    lesson_text = f"- {l.get('title','Lesson')} ({l.get('type','')})"
                    ctk.CTkLabel(m_frame, text=lesson_text, wraplength=620).pack(anchor="w", padx=18)
                    # show resources (if any)
                    resources = l.get("resources", [])
                    if resources:
                        for r in resources:
                            rtxt = f"   • [{r.get('type','')}] {r.get('name','')} - {r.get('url','') or ''}"
                            ctk.CTkLabel(m_frame, text=rtxt, text_color="gray", wraplength=620).pack(anchor="w", padx=28, pady=(0,2))

        # Footer actions
        footer = ctk.CTkFrame(dlg)
        footer.pack(fill="x", padx=12, pady=8)

        # If current user is instructor for this course or admin, show Manage button
        can_manage = False
        try:
            if user:
                role = getattr(user, 'role', None)
                # Robust ID extraction
                uid = getattr(user, 'id', None)
                if not uid:
                    uid = getattr(user, '_id', None)
                uid = str(uid) if uid else ""

                if role == 'admin' or (role == 'instructor' and uid and uid == str(course.get('instructorId'))):
                    can_manage = True
        except Exception as e:
            print(f"Error checking manage permissions in details: {e}")
            can_manage = False

        if can_manage:
            def go_manage():
                dlg.destroy()
                manage_page = self.page_manager.get_page('manage_course')
                manage_page.set_course(course_id)
                self.page_manager.show_page('manage_course')

            ctk.CTkButton(footer, text="Manage Course", command=go_manage, fg_color="blue").pack(side="left", padx=6)

        # Enroll button for students
        if user and getattr(user, 'role', None) == 'student':
            def enroll():
                success = self.enrollment_service.enroll_student(user, course_id)
                if success:
                    ctk.CTkLabel(footer, text="Enrollment request sent!", text_color="green").pack(side="left", padx=6)
                else:
                    ctk.CTkLabel(footer, text="Already requested or enrolled.", text_color="orange").pack(side="left", padx=6)
            ctk.CTkButton(footer, text="Request Enrollment", command=enroll, fg_color="blue").pack(side="left", padx=6)

        # Enroll or Close
        def close():
            dlg.destroy()

        ctk.CTkButton(footer, text="Close", command=close).pack(side="right", padx=6)

    def refresh_courses(self):
        """Clear and repopulate the courses list"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if self.filter_mode == "instructor" and self.filter_id:
            courses = self.course_service.get_courses_by_instructor(self.filter_id)
            self.title_label.configure(text="My Courses")
        else:
            courses = self.course_service.get_published_courses()
            self.title_label.configure(text="Available Courses")

        if not courses:
            no_courses_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No courses available yet.",
                font=("Arial", 14),
                text_color="gray"
            )
            no_courses_label.pack(pady=20)
            return

        for course in courses:
            self.create_course_card(self.scroll_frame, course)

    def on_show(self):
        """Called by PageManager when this page is shown; refresh the list."""
        try:
            self.refresh_courses()
        except Exception:
            pass

    def show_edit_dialog(self, course):
        """Open a simple edit dialog for title/description/category/status"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Course")
        dialog.geometry("480x420")

        form = ctk.CTkFrame(dialog)
        form.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        ctk.CTkLabel(form, text="Title:").pack(anchor="w", pady=(0,5))
        title_entry = ctk.CTkEntry(form)
        title_entry.pack(fill="x", pady=5)
        title_entry.insert(0, course.get("title", ""))

        # Description
        ctk.CTkLabel(form, text="Description:").pack(anchor="w", pady=(10,5))
        desc_txt = ctk.CTkTextbox(form, height=120)
        desc_txt.pack(fill="both", pady=5)
        desc_txt.insert("1.0", course.get("description", ""))

        # Category
        ctk.CTkLabel(form, text="Category:").pack(anchor="w", pady=(10,5))
        category_entry = ctk.CTkEntry(form)
        category_entry.pack(fill="x", pady=5)
        category_entry.insert(0, course.get("category", ""))

        # Status
        ctk.CTkLabel(form, text="Status:").pack(anchor="w", pady=(10,5))
        status_combo = ctk.CTkComboBox(form, values=["published", "draft"], state="readonly")
        status_combo.pack(fill="x", pady=5)
        status_combo.set(course.get("status", "draft"))

        def save_changes():
            updates = {
                "title": title_entry.get().strip(),
                "description": desc_txt.get("1.0", "end").strip(),
                "category": category_entry.get().strip(),
                "status": status_combo.get()
            }
            ok = self.course_service.update_course(course.get("id"), updates)
            if ok:
                dialog.destroy()
                self.refresh_courses()
            else:
                # show a small error label
                err = ctk.CTkLabel(form, text="Failed to save changes", text_color="red")
                err.pack(pady=5)

        save_btn = ctk.CTkButton(form, text="Save", command=save_changes, fg_color="green")
        save_btn.pack(pady=(12, 5))
        
        def go_manage():
            dialog.destroy()
            manage_page = self.page_manager.get_page('manage_course')
            manage_page.set_course(course.get("id"))
            self.page_manager.show_page('manage_course')

        manage_btn = ctk.CTkButton(form, text="Manage Content", command=go_manage, fg_color="blue")
        manage_btn.pack(pady=5)

    def confirm_delete(self, course_id: str):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Confirm Delete")
        dlg.geometry("360x140")
        ctk.CTkLabel(dlg, text="Are you sure you want to delete this course?", wraplength=320).pack(pady=12, padx=12)

        def do_delete():
            ok = self.course_service.delete_course(course_id)
            if ok:
                dlg.destroy()
                self.refresh_courses()
            else:
                ctk.CTkLabel(dlg, text="Failed to delete course", text_color="red").pack()

        btns = ctk.CTkFrame(dlg)
        btns.pack(pady=8)
        ctk.CTkButton(btns, text="Delete", command=do_delete, fg_color="red").pack(side="left", padx=8)
        ctk.CTkButton(btns, text="Cancel", command=dlg.destroy).pack(side="left", padx=8)
    
    def go_back(self):
        """Go back to dashboard"""
        self.page_manager.show_page("dashboard")
