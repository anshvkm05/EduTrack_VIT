from flask_login import LoginManager, UserMixin

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Please sign in to access EduTrack VIT."
login_manager.login_message_category = "error"


class AdminUser(UserMixin):
    """Lightweight user model for Flask-Login (admins table)."""

    def __init__(self, id: int, username: str):
        self.id = id
        self.username = username
