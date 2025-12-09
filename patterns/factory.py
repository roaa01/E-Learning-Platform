class UserFactory:
    @staticmethod
    def create_user(user_type, **kwargs):
        # Import user classes lazily to avoid circular imports with models.user
        from models.user import Student, Instructor, Admin

        if user_type == "student":
            return Student(**kwargs)
        elif user_type == "instructor":
            return Instructor(**kwargs)
        elif user_type == "admin":
            return Admin(**kwargs)
        else:
            raise ValueError(f"Unknown user type: {user_type}")
        