import os
from django.core.files.storage import FileSystemStorage

STATE_CHOICES = [
    (0, "Hidden"),
    (1, "Disabled"),
    (2, "Enabled"),
]

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name
