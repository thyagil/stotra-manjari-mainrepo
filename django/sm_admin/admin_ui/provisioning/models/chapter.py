from django.db import models
from .project import Project
from .volume import Volume
from .base import STATE_CHOICES

class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="chapters", null=True, blank=True)
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, related_name="chapters", null=True, blank=True)

    index = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    state = models.IntegerField(default=2, choices=STATE_CHOICES)

    class Meta:
        ordering = ["index"]
        unique_together = ("volume", "code")

    def __str__(self):
        parent = self.volume.name if self.volume else self.project.project_name
        return f"{parent} - {self.title or self.code}"
