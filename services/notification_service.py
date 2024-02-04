import os

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class NotificationService(metaclass=SingletonMeta):
    def __init__(self):
        # Email setup from environment variables for enhanced security
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))  # Default to 587 if SMTP_PORT is not set
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

# Usage
notification_service = NotificationService()
