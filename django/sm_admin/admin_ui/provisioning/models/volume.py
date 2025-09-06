import os
from django.db import models
from .project import Project

def volume_thumbnail_path(instance, filename):
    project_code = instance.project.code
    volume_code = instance.code
    ext = filename.split(".")[-1].lower()
    return os.path.join(project_code, "images", volume_code, f"thumbnail.{ext}")

class Volume(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="volumes")
    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=volume_thumbnail_path, blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.project.project_name} - {self.name} ({self.code})"
