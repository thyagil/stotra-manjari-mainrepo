from django.db import models
from .project import Project
from .artist import Artist

class Contributor(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="contributors")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="contributions")
    role = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.artist.full_name} - {self.role} ({self.project.project_name})"
