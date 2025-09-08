from django.db import models

class OrchestrationTask(models.Model):
    TASK_TYPES = [
        ("audio", "Audio Extraction"),
        ("content", "Content Generation"),
        ("durations", "Durations Extraction"),
        ("meanings", "Meanings Generation"),
    ]

    project = models.ForeignKey(
        "stotra_manjari_admin.Project",
        on_delete=models.CASCADE,
        related_name="orchestration_tasks",
    )
    volume = models.ForeignKey(
        "stotra_manjari_admin.Volume",
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    chapter = models.ForeignKey(
        "stotra_manjari_admin.Chapter",
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    input_params = models.JSONField(default=dict)  # flexible field for paths, formats, etc.
    status = models.CharField(max_length=20, default="pending")  # pending, running, success, failed
    log = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_task_type_display()} ({self.status})"
