from django.contrib import admin
from ..models.orchestration import OrchestrationTask

@admin.register(OrchestrationTask)
class OrchestrationTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "task_type", "status", "created_at", "updated_at")
    list_filter = ("task_type", "status", "created_at")
    search_fields = ("project__project_name", "log")
    readonly_fields = ("created_at", "updated_at")
