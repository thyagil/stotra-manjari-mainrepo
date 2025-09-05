from django.db import models
from django.utils import timezone
from provisioning.models import Project

STATUS_CHOICES = [
    ("pending", "Pending"),
    ("running", "Running"),
    ("success", "Success"),
    ("failed", "Failed"),
]

class PreStagingToStaging(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pre_to_stage_deployments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    log_path = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Pre-staging → Staging"
        verbose_name_plural = "Pre-staging → Staging"

    def __str__(self):
        return f"Pre-Staging → Staging - {self.project.project_name}"


class StagingToProduction(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="stage_to_prod_deployments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    log_path = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Staging → Production"
        verbose_name_plural = "Staging → Production"

    def __str__(self):
        return f"Staging → Production - {self.project.project_name}"
