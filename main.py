import customtkinter as ctk
from database.authservice import auth_servise
from patterns.factory import UserFactory
from database.seed import init_db, get_database, ensure_collections_and_indexes

# Initialize and seed the database
db = init_db()
ensure_collections_and_indexes()

if db is not None:
    users_collection = db.get_collection("users")
    service = auth_servise(users_collection)
    # Now you can use service.sign_up(...) and service.log_in(...)
else:
    print("Database connection failed. Authentication will not work.")

# -----------------------------
# CustomTkinter Setup
# -----------------------------
ctk.set_appearance_mode("dark")        # "dark" / "light" / "system"
ctk.set_default_color_theme("blue")    # "blue", "green", "dark-blue"

app = ctk.CTk()
app.title("E-Learning Auth System")
app.geometry("400x420")


# -----------------------------
# UI Elements
# -----------------------------
title_label = ctk.CTkLabel(
    app, text="User Authentication", font=("Arial", 22, "bold")
)
title_label.pack(pady=20)


# Role Dropdown
role_label = ctk.CTkLabel(app, text="Role")
role_label.pack()

role_option = ctk.CTkComboBox(
    app, values=["Student", "Instructor", "Admin"],
)
role_option.pack(pady=5)


# name
name_label = ctk.CTkLabel(app, text="name")
name_label.pack()

name_entry = ctk.CTkEntry(app, width=250)
name_entry.pack(pady=5)


# Email
email_label = ctk.CTkLabel(app, text="Email")
email_label.pack()

email_entry = ctk.CTkEntry(app, width=250)
email_entry.pack(pady=5)


# Password
password_label = ctk.CTkLabel(app, text="Password")
password_label.pack()

password_entry = ctk.CTkEntry(app, show="*", width=250)
password_entry.pack(pady=5)


# -----------------------------
# Button Handlers
# -----------------------------
def handle_signup():
    # Normalize role to expected lowercase values used by the service/factory
    raw_role = role_option.get()
    role = (raw_role or "").strip().lower()
    if role == "":
        role = "student"
    name = name_entry.get()
    email = email_entry.get()
    password = password_entry.get()

    user = service.sign_up(role, name, email, password)

    if user:
        msg_label.configure(text=f"Sign up success: {user.name}", text_color="green")
    else:
        msg_label.configure(text="Sign up failed", text_color="red")


def handle_login():
    email = email_entry.get()
    password = password_entry.get()

    user = service.log_in(email, password)
    print("trying to login",email,password)
    if user:
        msg_label.configure(
            text=f"Logged in: {user.name} ({user.role})",
            text_color="green"            
        )

    else:
        msg_label.configure(text="Login failed", text_color="red")


# -----------------------------
# Buttons
# -----------------------------
button_frame = ctk.CTkFrame(app)
button_frame.pack(pady=20)

signup_btn = ctk.CTkButton(button_frame, text="Sign Up", command=handle_signup)
signup_btn.grid(row=0, column=0, padx=10)

login_btn = ctk.CTkButton(button_frame, text="Log In", command=handle_login)
login_btn.grid(row=0, column=1, padx=10)


# Message Label
msg_label = ctk.CTkLabel(app, text="", font=("Arial", 14))
msg_label.pack(pady=10)


# -----------------------------
# Start the App
# -----------------------------
app.mainloop()
