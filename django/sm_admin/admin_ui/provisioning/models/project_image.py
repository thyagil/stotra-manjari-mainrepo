from django.db import models
from .project import Project

class ProjectImage(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    key = models.CharField(max_length=50)   # "cover", "banner", etc.
    path = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.project.project_name} - {self.key}"
