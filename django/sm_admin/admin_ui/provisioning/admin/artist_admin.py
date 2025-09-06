from django.contrib import admin
from provisioning.models import Artist


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name")
    list_display_links = ("full_name",)
    search_fields = ("full_name",)
