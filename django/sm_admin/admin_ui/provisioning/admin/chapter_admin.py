from django.contrib import admin
from provisioning.models import Chapter


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("index", "code", "title", "subtitle", "volume", "state")
    list_display_links = ("code",)
    list_filter = ("state", "volume", "project")
    search_fields = ("title", "code")
