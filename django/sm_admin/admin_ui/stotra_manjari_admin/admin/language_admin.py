from django.contrib import admin
from ..models import Language

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    list_display_links = ("name",)
    search_fields = ("name", "code")
