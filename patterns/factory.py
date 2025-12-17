class UserFactory:
    @staticmethod
    def create_user(user_type, **kwargs):
        # Import user classes lazily to avoid circular imports with models.user
        from models.user import Student, Instructor, Admin, UserRole

        # Normalize input to Enum
        try:
            # Handle if user_type is already an Enum or string
            if isinstance(user_type, UserRole):
                role_enum = user_type
            else:
                role_enum = UserRole(user_type.lower())
        except ValueError:
             raise ValueError(f"Unknown user type: {user_type}")

        if role_enum == UserRole.STUDENT:
            return Student(**kwargs)
        elif role_enum == UserRole.INSTRUCTOR:
            return Instructor(**kwargs)
        elif role_enum == UserRole.ADMIN:
            return Admin(**kwargs)
        else:
            raise ValueError(f"Unknown user type: {user_type}")
        