# driver/apps.py
from django.apps import AppConfig

class DriverConfig(AppConfig):
    name = 'driver'

    def ready(self):
        import driver.signals  # Ensure the signals are imported and registered
