from django.db import models
from django.utils import timezone
from provisioning.models import Project

STATUS_CHOICES = [
    ("pending", "Pending"),
    ("running", "Running"),
    ("success", "Success"),
    ("failed", "Failed"),
]

class AudioExtraction(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="audio_extractions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    log_path = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Audio Extraction - {self.project.project_name}"


class ContentGeneration(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="content_generations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    log_path = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Content Generation - {self.project.project_name}"


class DurationsExtraction(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="durations_extractions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    log_path = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Durations Extraction - {self.project.project_name}"


class MeaningsGeneration(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="meanings_generations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    log_path = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Meanings Generation - {self.project.project_name}"
