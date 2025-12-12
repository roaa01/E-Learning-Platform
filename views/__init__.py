from .auth_pages import AuthPage, LoginPage, SignupPage
from .student_dashboard import StudentDashboard, MyCoursesPage
from .instructor_dashboard import InstructorDashboard, EnrollmentRequestsPage
from .admin_dashboard import AdminDashboard
from .courses_page import CoursesPage
from .create_course_page import CreateCoursePage
from .manage_course_page import ManageCoursePage
from .manage_resources_page import ManageResourcesPage
from .page_manager import PageManager

__all__ = [
    'AuthPage', 'LoginPage', 'SignupPage',
    'StudentDashboard', 'MyCoursesPage',
    'InstructorDashboard', 'EnrollmentRequestsPage',
    'AdminDashboard',
    'CoursesPage', 'CreateCoursePage', 'ManageCoursePage', 'ManageResourcesPage',
    'PageManager'
]