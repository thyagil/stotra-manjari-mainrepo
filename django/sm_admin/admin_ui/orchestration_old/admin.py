from django.contrib import admin
from .models import AudioExtraction, ContentGeneration, DurationsExtraction, MeaningsGeneration
from django.utils.html import format_html
from django.urls import reverse

@admin.register(AudioExtraction)
class AudioExtractionAdmin(admin.ModelAdmin):
    list_display = ("project", "status", "started_at", "finished_at", "run_task_button")
    list_filter = ("status",)

    def run_task_button(self, obj):
        url = reverse("admin:run_audio", args=[obj.id])
        return format_html(f"<a class='button' href='{url}'>Run</a>")
    run_task_button.short_description = "Action"


@admin.register(ContentGeneration)
class ContentGenerationAdmin(admin.ModelAdmin):
    list_display = ("project", "status", "started_at", "finished_at")


@admin.register(DurationsExtraction)
class DurationsExtractionAdmin(admin.ModelAdmin):
    list_display = ("project", "status", "started_at", "finished_at")


@admin.register(MeaningsGeneration)
class MeaningsGenerationAdmin(admin.ModelAdmin):
    list_display = ("project", "status", "started_at", "finished_at")
