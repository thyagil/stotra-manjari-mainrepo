import csv
from django import forms
from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.utils.html import format_html

from provisioning.models import Volume, Chapter


class ChapterInlineForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = "__all__"
        widgets = {
            "index": forms.NumberInput(attrs={"style": "width:50px; text-align:center;"}),
            "title": forms.TextInput(attrs={"style": "width:80px;"}),
            "subtitle": forms.TextInput(attrs={"style": "width:350px;"}),
            "state" : forms.Select(attrs={"style": "width:80px;"})
        }

class ChapterInline(admin.TabularInline):
    model = Chapter
    form = ChapterInlineForm
    extra = 0
    fields = ("index", "title", "subtitle", "state", "code")
    readonly_fields = ("code",)
    ordering = ("index",)


class ChapterCSVImportForm(forms.Form):
    csv_file = forms.FileField()
    overwrite = forms.BooleanField(required=False, initial=False)


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ("code", "project", "name", "thumbnail_preview")
    readonly_fields = ("thumbnail_preview",)
    fields = ("project", "code", "name", "subtitle", "thumbnail", "thumbnail_preview")
    list_filter = ("project",)
    search_fields = ("name", "code")
    inlines = [ChapterInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:volume_id>/import_chapters/", self.admin_site.admin_view(self.import_chapters_view),
                 name="provisioning_volume_import_chapters"),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["import_chapters_url"] = reverse("admin:provisioning_volume_import_chapters", args=[object_id])
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def import_chapters_view(self, request, volume_id):
        volume = Volume.objects.get(pk=volume_id)
        project = volume.project
        prefix = project.chapter_prefix or "chapter_"
        label = project.chapter_label or "Chapter"

        if request.method == "POST":
            form = ChapterCSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data["csv_file"]
                overwrite = form.cleaned_data.get("overwrite", False)

                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.reader(decoded_file, delimiter="|")

                created_count, updated_count, skipped_count = 0, 0, 0
                for row in reader:
                    volume_number, chapter_number, subtitle = row
                    index = int(chapter_number)
                    chapter_code = f"{prefix}{index:03d}"
                    chapter_title = f"{label} {index}"

                    if overwrite:
                        chapter, created = Chapter.objects.update_or_create(
                            code=chapter_code, volume=volume,
                            defaults={"index": index, "title": chapter_title, "subtitle": subtitle, "state": 2},
                        )
                        if created: created_count += 1
                        else: updated_count += 1
                    else:
                        chapter, created = Chapter.objects.get_or_create(
                            code=chapter_code, volume=volume,
                            defaults={"index": index, "title": chapter_title, "subtitle": subtitle, "state": 2},
                        )
                        if created: created_count += 1
                        else: skipped_count += 1

                if overwrite:
                    messages.success(request, f"Imported {created_count}, updated {updated_count} chapters.")
                else:
                    messages.success(request, f"Imported {created_count}, skipped {skipped_count} chapters.")

                return redirect(f"../../{volume_id}/change/")
        else:
            form = ChapterCSVImportForm()

        context = {"form": form, "volume": volume, "opts": self.model._meta,
                   "title": f"Import Chapters into {volume.name}"}
        return render(request, "admin/provisioning/import_chapters.html", context)

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height: 75px;"/>', obj.thumbnail.url)
        return "No thumbnail"
    thumbnail_preview.short_description = "Thumbnail Preview"
