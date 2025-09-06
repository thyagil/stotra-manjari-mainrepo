from django.contrib import admin
from provisioning.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    list_display_links = ("name",)
    search_fields = ("name", "code")
