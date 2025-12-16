import customtkinter as ctk
from tkinter import filedialog, messagebox
from database.assignment_service import AssignmentService
from datetime import datetime

class AssignmentView(ctk.CTkToplevel):
    """Dialog for students to view assignment and submit work"""
    
    def __init__(self, master, assignment_id, student_id):
        super().__init__(master)
        self.assignment_id = assignment_id
        self.student_id = student_id
        self.service = AssignmentService()
        
        self.assignment = self.service.get_assignment(assignment_id)
        self.submission = self.service.get_submission(assignment_id, student_id)
        
        self.title("Assignment Details")
        self.geometry("600x600")
        
        if not self.assignment:
            ctk.CTkLabel(self, text="Assignment not found", text_color="red").pack(pady=20)
            return
            
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header, 
            text=self.assignment.get("title", "Untitled Assignment"), 
            font=("Arial", 20, "bold")
        ).pack(anchor="w")
        
        due_date = self.assignment.get("dueDate")
        due_str = due_date.strftime("%Y-%m-%d") if due_date else "No Due Date"
        
        ctk.CTkLabel(
            header,
            text=f"Due Date: {due_str} | Type: {self.assignment.get('submissionType', 'text').capitalize()}",
            text_color="gray"
        ).pack(anchor="w")
        
        # Instructions
        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(body, text="Instructions:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        
        instructions = ctk.CTkTextbox(body, height=100, fg_color="gray20", text_color="white")
        instructions.pack(fill="x", pady=5)
        instructions.insert("1.0", self.assignment.get("description", ""))
        instructions.configure(state="disabled")
        
        # Submission Section
        ctk.CTkLabel(body, text="Your Submission:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 5))
        
        if self.submission:
            status = self.submission.get("status", "submitted")
            status_color = "green" if status == "graded" else "blue"
            ctk.CTkLabel(body, text=f"Status: {status.capitalize()}", text_color=status_color).pack(anchor="w")
            
            if self.submission.get("grade") is not None:
                ctk.CTkLabel(body, text=f"Grade: {self.submission.get('grade')}", font=("Arial", 12, "bold")).pack(anchor="w")
            
            submitted_date = self.submission.get("submittedDate")
            if submitted_date:
                ctk.CTkLabel(body, text=f"Submitted on: {submitted_date.strftime('%Y-%m-%d %H:%M')}", text_color="gray", font=("Arial", 10)).pack(anchor="w")

        # Input Form
        self.create_submission_form(body)
        
    def create_submission_form(self, parent):
        sub_type = self.assignment.get("submissionType", "text")
        existing_content = self.submission.get("content", "") if self.submission else ""
        
        self.input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=10)
        
        if sub_type == "text":
            ctk.CTkLabel(self.input_frame, text="Enter your response:").pack(anchor="w")
            self.text_input = ctk.CTkTextbox(self.input_frame, height=150)
            self.text_input.pack(fill="x", pady=5)
            self.text_input.insert("1.0", existing_content)
            
        elif sub_type == "link":
            ctk.CTkLabel(self.input_frame, text="Paste your link:").pack(anchor="w")
            self.link_input = ctk.CTkEntry(self.input_frame, placeholder_text="https://...")
            self.link_input.pack(fill="x", pady=5)
            self.link_input.insert(0, existing_content)
            
        elif sub_type == "file":
            ctk.CTkLabel(self.input_frame, text="Upload File:").pack(anchor="w")
            file_row = ctk.CTkFrame(self.input_frame, fg_color="transparent")
            file_row.pack(fill="x", pady=5)
            
            self.file_path_entry = ctk.CTkEntry(file_row, placeholder_text="Select a file...")
            self.file_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
            self.file_path_entry.insert(0, existing_content)
            
            ctk.CTkButton(file_row, text="Browse", width=80, command=self.browse_file).pack(side="right")
            
        # Submit Button
        btn_text = "Update Submission" if self.submission else "Submit Assignment"
        ctk.CTkButton(
            self, 
            text=btn_text, 
            command=self.submit, 
            fg_color="green", 
            height=40
        ).pack(fill="x", padx=20, pady=20)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_path_entry.delete(0, "end")
            self.file_path_entry.insert(0, filename)
            
    def submit(self):
        sub_type = self.assignment.get("submissionType", "text")
        content = ""
        content_type = sub_type # Should match submission type usually
        
        if sub_type == "text":
            content = self.text_input.get("1.0", "end").strip()
            content_type = "text"
        elif sub_type == "link":
            content = self.link_input.get().strip()
            content_type = "link"
        elif sub_type == "file":
            content = self.file_path_entry.get().strip()
            content_type = "file"
            
        if not content:
            messagebox.showwarning("Warning", "Submission content cannot be empty")
            return
            
        success = self.service.submit_assignment(self.assignment_id, self.student_id, content, content_type)
        if success:
            messagebox.showinfo("Success", "Assignment submitted successfully!")
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to submit assignment")
