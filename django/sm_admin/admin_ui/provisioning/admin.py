import csv, json, os
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django import forms
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponseRedirect

from .models import (
    Project, Volume, Chapter, Artist, ProjectImage,
    Contributor, Category, Language
)

# ---------------------------
# Admin Branding
# ---------------------------
admin.site.site_header = "Stotra Manjari Admin"
admin.site.site_title = "Stotra Manjari Admin"
admin.site.index_title = "Welcome to Stotra Manjari Admin"

# ---------------------------
# Inlines
# ---------------------------
class VolumeInline(admin.TabularInline):
    model = Volume
    extra = 1

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

class ContributorInline(admin.TabularInline):
    model = Contributor
    extra = 1

# ---------------------------
# Project Admin
# ---------------------------
class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "categories": forms.SelectMultiple(attrs={"class": "select2"}),
            "languages": forms.SelectMultiple(attrs={"class": "select2"}),
        }
    class Media:
        css = {"all": ("css/custom_admin.css",)}
        js = ("js/project_image_preview.js",)   # 👈 add this

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ("id", "project_name", "code", "format", "published", "featured")
    list_filter = ("format", "published", "featured", "is_premium")
    search_fields = ("project_name", "code")

    readonly_fields = ("code", "generate_code_button", "cover_preview", "banner_preview")
    inlines = [ContributorInline]

    fieldsets = (
        (None, {
            "fields": (
                "project_name", "primary_artist",
                "code", "generate_code_button",
            )
        }),
        ("Details", {
            "fields": (
                "type", "format", "description", "overview", "preview",
                "featured", "published", "is_premium", "currency", "price",
                "categories", "languages",
            )
        }),
        ("Chapter Settings", {
            "fields": ("chapter_prefix", "chapter_label"),
            "classes": ("collapse",),
            "description": "Controls how chapter codes and titles are generated (e.g., sarga_001 / Sarga 1)."
        }),
        ("Project Images", {
            "fields": ("cover_image", "cover_preview", "banner_image", "banner_preview"),
            "classes": ("tab",),   # 👈 Jazzmin makes this a tab
        }),
    )

    def response_change(self, request, obj):
        # Always "Save and continue editing" behavior
        if "_save" in request.POST and not "_continue" in request.POST:
            post_url = reverse("admin:provisioning_project_change", args=[obj.pk])

            # Preserve Jazzmin's active tab (if sent)
            current_tab = request.GET.get("tab") or request.POST.get("tab")
            if current_tab:
                post_url += f"?tab={current_tab}"

            self.message_user(request, f"{obj} saved successfully. Staying on edit page.", messages.SUCCESS)
            return HttpResponseRedirect(post_url)

        return super().response_change(request, obj)
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img id="cover-preview" src="{}" style="height: 100px;"/>', obj.cover_image.url)
        return format_html('<img id="cover-preview" style="display:none; height:100px;"/>')

    cover_preview.short_description = "Cover Preview"

    def banner_preview(self, obj):
        if obj.banner_image:
            return format_html('<img id="banner-preview" src="{}" style="height: 100px;"/>', obj.banner_image.url)
        return format_html('<img id="banner-preview" style="display:none; height:100px;"/>')

    banner_preview.short_description = "Banner Preview"

    def save_model(self, request, obj, form, change):
        print("DEBUG >> cover_image raw:", request.FILES.get("cover_image"))
        print("DEBUG >> banner_image raw:", request.FILES.get("banner_image"))
        print("DEBUG >> form.cleaned_data.cover_image:", form.cleaned_data.get("cover_image"))
        print("DEBUG >> obj.cover_image before save:", obj.cover_image)
        super().save_model(request, obj, form, change)
        print("DEBUG >> obj.cover_image after save:", obj.cover_image)

    def get_readonly_fields(self, request, obj=None):
        ro_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # editing an existing project
            if obj.volumes.filter(chapters__isnull=False).exists():
                ro_fields.extend(["chapter_prefix", "chapter_label"])
        return ro_fields

    # custom URLs
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:project_id>/generate_code/",
                 self.admin_site.admin_view(self.generate_code_view),
                 name="provisioning_project_generate_code"),
            path("<int:project_id>/preview_marketplace/",
                 self.admin_site.admin_view(self.preview_marketplace),
                 name="provisioning_project_preview_marketplace"),
            path("<int:project_id>/preview_project/",
                 self.admin_site.admin_view(self.preview_project),
                 name="provisioning_project_preview_project"),
            path("<int:project_id>/publish_staging/",
                 self.admin_site.admin_view(self.publish_staging),
                 name="provisioning_project_publish_staging"),
        ]
        return custom_urls + urls

    # buttons
    def generate_code_button(self, obj):
        if obj and obj.pk:
            url = reverse("admin:provisioning_project_generate_code", args=[obj.pk])
            return format_html('<a class="button" href="{}">Generate</a>', url)
        return "Save project first"
    generate_code_button.short_description = "Generate Project Code"


# actions
    def generate_code_view(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        if project.primary_artist and project.project_name:
            artist_code = project.primary_artist.artist_code.lower()
            project_slug = project.project_name.lower().replace(" ", "_")
            project.code = f"{artist_code}_{project_slug}"
            project.save()
            messages.success(request, f"Project code generated: {project.code}")
        else:
            messages.error(request, "Please set primary artist and project name first.")

        return redirect(reverse("admin:provisioning_project_change", args=[project_id]))


    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["preview_marketplace_url"] = reverse(
            "admin:provisioning_project_preview_marketplace", args=[object_id]
        )
        extra_context["preview_project_url"] = reverse(
            "admin:provisioning_project_preview_project", args=[object_id]
        )
        extra_context["publish_staging_url"] = reverse(
            "admin:provisioning_project_publish_staging", args=[object_id]
        )
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


    # JSON builders
    def build_marketplace_json(self, project: Project):
        artist_name = ""
        if project.type in ["audio_book", "music_album"]:
            artist_name = project.primary_artist.formal_name or project.primary_artist.full_name if project.primary_artist else "[MISSING PRIMARY ARTIST]"
        return {
            "id": project.code,
            "project_name": project.project_name,
            "artist": artist_name,
            "description": project.description or "",
            "images": {
                "cover": project.cover_image.name if project.cover_image else "",
                "banner": project.banner_image.name if project.banner_image else "",
            },
            "type": project.type,
            "format": project.format,
            "featured": project.featured,
            "is_premium": project.is_premium,
        }

    def build_project_json(self, project: Project):
        artist_name = ""
        if project.type in ["audio_book", "music_album"] and project.primary_artist:
            artist_name = project.primary_artist.formal_name or project.primary_artist.full_name
        return {
            "id": project.code,
            "project_name": project.project_name,
            "type": project.type,
            "format": project.format,
            "description": project.description,
            "artist": artist_name,
            "category": [c.name for c in project.categories.all()],
            "languages": [l.code for l in project.languages.all()],
            "contributors": [
                {"role": c.role, "name": c.artist.formal_name or c.artist.full_name}
                for c in project.contributors.all()
            ],
            "overview": project.overview,
            "preview": project.preview,
            "images": {
                "cover": project.cover_image.name if project.cover_image else "",
                "banner": project.banner_image.name if project.banner_image else "",
            },
            "app_status": {
                "featured": project.featured,
                "published": project.published,
                "monetization": {
                    "isPremium": project.is_premium,
                    "currency": project.currency,
                    "price": project.price,
                },
            },
            "structure": {
                "volumes": [
                    {
                        "id": v.code,
                        "name": v.name,
                        "subtitle": v.subtitle,
                        "state": 2,
                        "images": {"thumbnail": v.thumbnail.name if v.thumbnail else ""},
                        "chapters": [
                            {"id": c.code, "index": c.index, "title": c.title, "subtitle": c.subtitle, "state": c.state}
                            for c in v.chapters.all()
                        ],
                    }
                    for v in project.volumes.all()
                ]
            },
        }

    # preview & publish views
    def preview_marketplace(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        return JsonResponse(self.build_marketplace_json(project), safe=False, json_dumps_params={"indent": 2})

    def preview_project(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        return JsonResponse(self.build_project_json(project), safe=False, json_dumps_params={"indent": 2})

    from django.conf import settings

    def publish_staging(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        project_json = self.build_project_json(project)
        marketplace_entry = self.build_marketplace_json(project)

        # project-specific metadata folder
        project_root = os.path.join(settings.PROJECT_ROOT, project.code, "metadata")
        os.makedirs(project_root, exist_ok=True)

        # write project.json
        project_path = os.path.join(project_root, "project.json")
        with open(project_path, "w", encoding="utf-8") as f:
            json.dump(project_json, f, indent=2, ensure_ascii=False)

        # write marketplace_snippet.json
        marketplace_path = os.path.join(project_root, "marketplace_snippet.json")
        with open(marketplace_path, "w", encoding="utf-8") as f:
            json.dump(marketplace_entry, f, indent=2, ensure_ascii=False)

        messages.success(
            request,
            f"Published {project.code} metadata to staging (project.json + marketplace_snippet.json)."
        )
        return redirect(f"../../{project_id}/change/")


    def get_inlines(self, request, obj=None):
        if obj:
            if obj.format == "volume":
                return [VolumeInline, ContributorInline]
            elif obj.format == "chapter":
                return [ChapterInline, ContributorInline]
            else:  # standalone
                return [ContributorInline]
        return super().get_inlines(request, obj)

# ---------------------------
# Volume Admin
# ---------------------------
class ChapterCSVImportForm(forms.Form):
    csv_file = forms.FileField()

@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "code", "name", "thumbnail_preview")
    readonly_fields = ("thumbnail_preview",)
    fields = ("project", "code", "name", "subtitle", "thumbnail", "thumbnail_preview")
    list_filter = ("project",)
    search_fields = ("name", "code")
    inlines = [ChapterInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:volume_id>/import_chapters/",
                 self.admin_site.admin_view(self.import_chapters_view),
                 name="provisioning_volume_import_chapters"),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        try:
            url = reverse("admin:provisioning_volume_import_chapters", args=[object_id])
            print("DEBUG >> Import Chapters URL:", url)
            extra_context["import_chapters_url"] = url
        except Exception as e:
            print("DEBUG >> Reverse failed:", e)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def import_chapters_view(self, request, volume_id):
        volume = Volume.objects.get(pk=volume_id)
        project = volume.project  # 👈 get related project

        prefix = project.chapter_prefix or "chapter_"
        label = project.chapter_label or "Chapter"

        if request.method == "POST":
            form = ChapterCSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data["csv_file"]
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.reader(decoded_file)

                created_count, skipped_count = 0, 0
                for row in reader:
                    volume_number, chapter_number, subtitle = row
                    index = int(chapter_number)
                    chapter_code = f"{prefix}{index:03d}"   # 👈 prefix used here
                    chapter_title = f"{label} {index}"

                    chapter, created = Chapter.objects.get_or_create(
                        code=chapter_code,
                        volume=volume,
                        defaults={"index": index,
                                  "title": f"{label} {index}",
                                  "subtitle": subtitle,
                                  "state": 2},
                    )
                    created_count += 1 if created else 0
                    skipped_count += 0 if created else 1

                messages.success(request, f"Imported {created_count} chapters, skipped {skipped_count} existing ones.")
                return redirect(f"../../{volume_id}/change/")
        else:
            form = ChapterCSVImportForm()

        context = {"form": form, "volume": volume, "opts": self.model._meta, "title": f"Import Chapters into {volume.name}"}
        return render(request, "admin/provisioning/import_chapters.html", context)

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height: 75px;"/>', obj.thumbnail.url)
        return "No thumbnail"
    thumbnail_preview.short_description = "Thumbnail Preview"

# ---------------------------
# Simple Admins
# ---------------------------
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "index", "title", "volume", "project", "state")
    list_filter = ("state", "volume", "project")
    search_fields = ("title", "code")

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name")
    search_fields = ("full_name",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    search_fields = ("name", "code")

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    search_fields = ("name", "code")
