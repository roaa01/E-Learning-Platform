import customtkinter as ctk
from database.authservice import auth_servise
from patterns.factory import UserFactory
from database.seed import init_db, get_database, ensure_collections_and_indexes

# Import the page manager and pages
from views.page_manager import PageManager
from views.auth_page import AuthPage
from views.login import LoginPage
from views.signup import SignupPage
from views.dashboard_page import DashboardPage
from views.courses_page import CoursesPage
from views.create_course_page import CreateCoursePage
from views.manage_course_page import ManageCoursePage
from views.manage_resources_page import ManageResourcesPage

# -----------------------------
# Database Setup
# -----------------------------
db = init_db()
ensure_collections_and_indexes()

if db is not None:
    users_collection = db.get_collection("users")
    service = auth_servise(users_collection)
else:
    print("Database connection failed. Authentication will not work.")
    exit(1)

# -----------------------------
# CustomTkinter Setup
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("E-Learning Auth System")
app.geometry("500x600")

# -----------------------------
# Page Manager Setup
# -----------------------------
page_manager = PageManager(app)

# Register ALL pages at startup
page_manager.add_page("auth", lambda master, pm: AuthPage(master, pm, service))
page_manager.add_page("login", lambda master, pm: LoginPage(master, pm, service))
page_manager.add_page("signup", lambda master, pm: SignupPage(master, pm, service))
page_manager.add_page("dashboard", DashboardPage)
page_manager.add_page("courses", CoursesPage)
page_manager.add_page("create_course", CreateCoursePage)
page_manager.add_page("manage_course", ManageCoursePage)
page_manager.add_page("manage_resources", ManageResourcesPage)

# Show initial page (auth page)
page_manager.show_page("auth")

# -----------------------------
# Start the App
# -----------------------------
app.mainloop()