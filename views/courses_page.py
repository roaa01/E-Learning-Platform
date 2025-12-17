import customtkinter as ctk
from database.course_service import CourseService
from database.EnrollmentService import EnrollmentService
from models.user import Student
from database.seed import get_database
from models.SearchCriteria import SearchCriteria
from patterns.search.filter_search_strategy import FilterSearchStrategy
from patterns.search.recommendation_search_strategy import RecommendationSearchStrategy
from patterns.search.search_context import SearchContext
from database.category_service import CategoryService
from database.authservice import AuthService

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
        self.search_strategy = FilterSearchStrategy()
        self.search_context = SearchContext(self.search_strategy)
        self.category_service = CategoryService() # For populating dropdown
        # Initialize AuthService for instructor lookup
        db = get_database()
        self.auth_service = AuthService(db.get_collection("users"))
        
        # Pagination & Recommendation State
        self.recommendation_strategy = RecommendationSearchStrategy()
        self.is_recommendation_mode = False
        self.current_page = 1
        self.page_size = 5
        
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
        
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=20, fill="x", expand=True)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search courses...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        search_btn = ctk.CTkButton(search_frame, text="Search", command=self.perform_search, width=60)
        search_btn.pack(side="left")

        # More Filters (Expandable or just visible row)
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="left", padx=10, fill="x")

        # Category ComboBox
        categories = self.category_service.get_all_categories()
        # Create a map for name lookup by ID
        self.category_map = {c.get("categoryId"): c.get("name") for c in categories}
        
        cat_names = [c.get("name", "Unknown") for c in categories]
        cat_names.insert(0, "All Categories")
        
        self.cat_combo = ctk.CTkComboBox(filter_frame, values=cat_names, width=150)
        self.cat_combo.pack(side="left", padx=5)
        self.cat_combo.set("All Categories")

        # Recommendation Toggle Button
        self.rec_btn = ctk.CTkButton(
            filter_frame,
            text="Show Recommended",
            command=self.toggle_recommendation,
            width=140,
            fg_color="gray",  # Default inactive color
            hover_color="gray40"
        )
        self.rec_btn.pack(side="left", padx=10)

        back_btn = ctk.CTkButton(
            header_frame,
            text="Back",
            command=self.go_back,
            width=80
        )
        back_btn.pack(side="right")
        
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="Refresh",
            command=self.on_show,
            width=80
        )
        refresh_btn.pack(side="right", padx=5)
        
        # Scrollable courses container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Pagination Controls
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(pady=10, fill="x")
        
        self.prev_btn = ctk.CTkButton(self.pagination_frame, text="Previous", width=80, command=self.prev_page)
        self.prev_btn.pack(side="left", padx=20)
        
        self.page_label = ctk.CTkLabel(self.pagination_frame, text="Page 1", font=("Arial", 12, "bold"))
        self.page_label.pack(side="left", expand=True)
        
        self.next_btn = ctk.CTkButton(self.pagination_frame, text="Next", width=80, command=self.next_page)
        self.next_btn.pack(side="right", padx=20)

        self.filter_mode = "all"  # or "instructor"
        self.filter_id = None
        self.current_search_query = ""

    def set_mode(self, mode="all", filter_id=None):
        self.filter_mode = mode
        self.filter_id = filter_id
        self.refresh_courses()

    def filter_by_instructor(self, instructor_id, instructor_name):
        """Set filter to specific instructor and refresh"""
        self.current_instructor_filter = instructor_id
        self.current_instructor_name = instructor_name
        self.is_recommendation_mode = False # Disable rec mode when filtering specific
        self.current_page = 1
        self.refresh_courses()
        
    def toggle_recommendation(self):
        """Switch between standard search and recommendation mode"""
        self.is_recommendation_mode = not self.is_recommendation_mode
        self.current_page = 1 # Reset page
        
        # Update button visual state
        if self.is_recommendation_mode:
            self.rec_btn.configure(text="Show All Courses", fg_color="#1f538d") # Active color
        else:
            self.rec_btn.configure(text="Show Recommended", fg_color="gray")
            
        self.refresh_courses()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_courses()

    def next_page(self):
        self.current_page += 1
        self.refresh_courses()

    def perform_search(self):
        query = self.search_entry.get().strip()
        self.current_search_query = query
        # Reset instructor filter on new manual search? 
        # Usually yes, or keep it combined. Let's reset for clarity unless we want advanced composition.
        # User request: "click ... show all the instructor courses". Implies filtering by THAT instructor.
        # If I type "Python" and click search, I expect to search "Python" in ALL courses or current view?
        # Let's keep filters composite BUT if I search manually, I might want to clear the specific instructor click?
        # Let's keep it simple: Perform Search respects the current visual inputs (dropdown/text).
        # The instructor filter is "hidden" state from the click. 
        # I will CLEAR the clicked instructor filter when hitting Search to avoid confusion, 
        # OR I should show a chip. 
        # For simplicity: Search button RESETS the clicked instructor filter.
        self.current_instructor_filter = None 
        self.is_recommendation_mode = False # Search exits rec mode
        self.current_page = 1
        self.refresh_courses()

    def send_enrollment_request(self, student, course_id):
        """Call EnrollmentService to send an enrollment request for a student and provide feedback."""
        success = self.enrollment_service.enroll_student(student, course_id)
        return success
    
    def get_enrollment_status(self, student_id, course_id):
        """Check if student is enrolled/pending/rejected for a course"""
        from bson import ObjectId
        db = get_database()
        enrollments = db.get_collection("enrollments")
        
        try:
            enrollment = enrollments.find_one({
                "student_id": ObjectId(student_id),
                "course_id": course_id
            })
            if enrollment:
                return enrollment.get("status", "pending")
        except Exception as e:
            print(f"Error checking enrollment status: {e}")
        return None
    
    def handle_reapply(self, user, course_id, parent_widget):
        """Delete rejected enrollment and create new pending request"""
        from bson import ObjectId
        db = get_database()
        enrollments = db.get_collection("enrollments")
        
        try:
            # Delete the rejected enrollment
            enrollments.delete_one({
                "student_id": ObjectId(user.id),
                "course_id": course_id
            })
            # Create new enrollment request
            success = self.enrollment_service.enroll_student(user, course_id)
            if success:
                # Refresh the page to show updated status
                self.on_show()
        except Exception as e:
            print(f"Error re-applying: {e}")

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
        
        # Resolve category name
        cat_id = course.get("categoryId")
        cat_name = self.category_map.get(cat_id)
        if not cat_name:
            cat_name = course.get("category", "N/A")

        category = ctk.CTkLabel(
            info_frame,
            text=f"Cat: {cat_name}",
            font=("Arial", 10),
            text_color="lightblue"
        )
        category.pack(side="left", padx=5)
        
        # Instructor Name (Clickable)
        instr_id = course.get("instructorId")
        instr_name = "Unknown"
        if instr_id:
            try:
                # Fetch user doc
                u = self.auth_service.get_user_by_id(instr_id)
                if u:
                    # User object returned, access attributes directly
                    instr_name = getattr(u, "name", None) or getattr(u, "full_name", None) or getattr(u, "email", None) or "Instructor"
            except Exception as e:
                print(f"Error fetching instructor: {e}")
                pass
        
        instr_label = ctk.CTkLabel(
            info_frame,
            text=f"By: {instr_name}",
            font=("Arial", 10, "underline"),
            text_color="lightblue",
            cursor="hand2"
        )
        instr_label.pack(side="left", padx=5)
        # Bind click event
        if instr_id:
            instr_label.bind("<Button-1>", lambda e: self.filter_by_instructor(instr_id, instr_name))

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
            # Check enrollment status
            enrollment_status = self.get_enrollment_status(str(user.id), course.get("id"))
            
            if enrollment_status == "approved":
                status_label = ctk.CTkLabel(actions, text="✓ Enrolled", text_color="lightgreen", font=("Arial", 12, "bold"))
                status_label.pack(side="right", padx=5)
            elif enrollment_status == "pending":
                status_label = ctk.CTkLabel(actions, text="⏳ Pending Approval", text_color="orange", font=("Arial", 12))
                status_label.pack(side="right", padx=5)
            elif enrollment_status == "rejected":
                status_label = ctk.CTkLabel(actions, text="✗ Rejected", text_color="red", font=("Arial", 12))
                status_label.pack(side="right", padx=5)
                reapply_btn = ctk.CTkButton(actions, text="Re-apply", command=lambda: self.handle_reapply(user, course.get("id"), actions), width=80, height=28, fg_color="orange")
                reapply_btn.pack(side="right", padx=5)
            else:
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

        courses = []
        
        # Prepare Criteria for cases that use it
        criteria = SearchCriteria(
            page=self.current_page,
            page_size=self.page_size
        )

        if self.filter_mode == "instructor" and self.filter_id:
            # Instructor Dashboard View (My Courses)
            # This remains a direct service call as it's a specific "management" view 
            # rather than a "search" view, but could be refactored into a strategy later.
            courses = self.course_service.get_courses_by_instructor(self.filter_id)
            self.title_label.configure(text="My Courses")
        
        else:
            # Use SearchContext for both Recommendation and Standard modes
            
            if self.is_recommendation_mode:
                 # Switch to Recommendation Strategy
                self.search_context.set_strategy(self.recommendation_strategy)
                criteria.sort_by = "recommended"
                self.title_label.configure(text="Recommended for You")
            else:
                # Switch to Standard Filter Strategy
                self.search_context.set_strategy(self.search_strategy)
                
                # ... existing param logic ...
                query = getattr(self, "current_search_query", "")
                cat_filter = None
                if hasattr(self, 'cat_combo'):
                    val = self.cat_combo.get()
                    if val and val != "All Categories":
                        cat_filter = val
                instr_filter = getattr(self, 'current_instructor_filter', None) 
                
                criteria.query = query if query else None
                criteria.category = cat_filter if cat_filter else None
                criteria.instructor_id = instr_filter if instr_filter else None
                
                # Update Title
                title_parts = []
                if query: title_parts.append(f"Query: '{query}'")
                if cat_filter: title_parts.append(f"Category: '{cat_filter}'")
                if instr_filter: 
                    name = getattr(self, 'current_instructor_name', instr_filter)
                    title_parts.append(f"Instructor: '{name}'")
                
                if not title_parts:
                    self.title_label.configure(text="Available Courses")
                else:
                    self.title_label.configure(text=f"Results: {', '.join(title_parts)}")

            # Execute via Context
            course_objects = self.search_context.execute_search(criteria)
            courses = [c.to_dict() for c in course_objects]

        # Update Pagination UI
        self.page_label.configure(text=f"Page {self.current_page}")
        
        # Disable Previous if on page 1
        if self.current_page <= 1:
            self.prev_btn.configure(state="disabled", fg_color="gray")
        else:
            self.prev_btn.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"])
            
        # Disable Next if we got fewer results than page_size (end of list)
        if len(courses) < self.page_size:
            self.next_btn.configure(state="disabled", fg_color="gray")
        else:
            self.next_btn.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"])

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
