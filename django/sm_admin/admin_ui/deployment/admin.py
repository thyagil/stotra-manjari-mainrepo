from django.contrib import admin
from .models import PreStagingToStaging, StagingToProduction
from django.utils.html import format_html
from django.urls import reverse

@admin.register(PreStagingToStaging)
class PreStagingToStagingAdmin(admin.ModelAdmin):
    list_display = ("project", "status", "started_at", "finished_at", "run_deploy_button")

    def run_deploy_button(self, obj):
        url = reverse("admin:run_pre_to_stage", args=[obj.id])
        return format_html(f"<a class='button' href='{url}'>Run</a>")
    run_deploy_button.short_description = "Action"


@admin.register(StagingToProduction)
class StagingToProductionAdmin(admin.ModelAdmin):
    list_display = ("project", "status", "started_at", "finished_at", "run_deploy_button")

    def run_deploy_button(self, obj):
        url = reverse("admin:run_stage_to_prod", args=[obj.id])
        return format_html(f"<a class='button' href='{url}'>Run</a>")
    run_deploy_button.short_description = "Action"
