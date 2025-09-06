import os, json
from django import forms
from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.html import format_html
from django.conf import settings
from django.utils.safestring import mark_safe
import csv

from provisioning.models import Project, Contributor, Volume, Chapter


# --- Inlines ---
class VolumeInline(admin.TabularInline):
    model = Volume
    extra = 0
    classes = ("tab-volumes",)
    fields = ("code", "name", "subtitle", "thumbnail_preview")
    readonly_fields = ("code", "thumbnail_preview")
    ordering = ("code",)

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height: 75px;"/>', obj.thumbnail.url)
        return "No thumbnail"
    thumbnail_preview.short_description = "Thumbnail Preview"


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    classes = ("tab-chapters",)


class ContributorInline(admin.TabularInline):
    model = Contributor
    extra = 0
    classes = ("tab-contributors",)  # 👈 contributors get their own tab


# --- Form ---
class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "categories": forms.SelectMultiple(attrs={"class": "select2"}),
            "languages": forms.SelectMultiple(attrs={"class": "select2"}),
        }

    class Media:
        js = ("js/project_image_preview.js",)

class VolumeCSVImportForm(forms.Form):
    csv_file = forms.FileField()
    overwrite = forms.BooleanField(
        required=False,
        initial=False,
        help_text="If checked, existing volumes will be overwritten."
    )

# --- Project Admin ---
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ("id", "project_name", "code", "format", "published", "featured")
    list_display_links = ("project_name",)
    list_filter = ("format", "published", "featured", "is_premium")
    search_fields = ("project_name", "code")

    readonly_fields = ("code", "code_with_button", "cover_preview", "banner_preview")

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "project_name",
                "primary_artist",
                "code_with_button",
                "chapter_prefix",
                "chapter_label",
            ),
            "classes": ("tab-basic",),
        }),
        ("Details", {
            "fields": (
                "type", "format", "description", "overview", "preview",
                "featured", "published", "is_premium", "currency", "price",
                "categories", "languages",
            ),
            "classes": ("tab-details",),
        }),
        ("Project Images", {
            "fields": ("cover_image", "cover_preview", "banner_image", "banner_preview"),
            "classes": ("tab-images",),
        }),
    )

    inlines = [VolumeInline, ContributorInline]  # ✅ simple: volumes + contributors

    # --- Code field with Generate button ---
    def code_with_button(self, obj):
        if not obj or not obj.pk:
            return "Save project first to generate code."

        code_input = f'<input type="text" name="code" value="{obj.code or ""}" style="width:200px;" />'
        url = reverse("admin:provisioning_project_generate_code", args=[obj.pk])
        generate_btn = f'<a class="button" href="{url}" title="Generate project code" style="padding:2px 8px;">⚙️</a>'

        return mark_safe(f"""
            <div style="display:flex;align-items:center;gap:6px;">
                {code_input}
                {generate_btn}
            </div>
        """)

    code_with_button.short_description = "Project Code"

    # --- Keep tab position after save ---
    def response_change(self, request, obj):
        if "_save" in request.POST and not "_continue" in request.POST:
            post_url = reverse("admin:provisioning_project_change", args=[obj.pk])
            current_tab = request.GET.get("tab") or request.POST.get("tab")
            if current_tab:
                post_url += f"?tab={current_tab}"
            self.message_user(request, f"{obj} saved successfully. Staying on edit page.", messages.SUCCESS)
            return HttpResponseRedirect(post_url)
        return super().response_change(request, obj)

    # --- Image previews ---
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

    # --- Custom URLs ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:project_id>/generate_code/", self.admin_site.admin_view(self.generate_code_view),
                 name="provisioning_project_generate_code"),
            path(
                "<int:project_id>/import_volumes/",
                self.admin_site.admin_view(self.import_volumes_view),
                name="provisioning_project_import_volumes",
            ),
            path("<int:project_id>/preview_marketplace/", self.admin_site.admin_view(self.preview_marketplace),
                 name="provisioning_project_preview_marketplace"),
            path("<int:project_id>/preview_project/", self.admin_site.admin_view(self.preview_project),
                 name="provisioning_project_preview_project"),
            path("<int:project_id>/publish_staging/", self.admin_site.admin_view(self.publish_staging),
                 name="provisioning_project_publish_staging"),
        ]
        return custom_urls + urls

    def generate_code_button(self, obj):
        if obj and obj.pk:
            url = reverse("admin:provisioning_project_generate_code", args=[obj.pk])
            return format_html('<a class="button" href="{}">Generate</a>', url)
        return "Save project first"
    generate_code_button.short_description = "Generate Project Code"

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

    def import_volumes_view(self, request, project_id):
        project = Project.objects.get(pk=project_id)

        if request.method == "POST":
            form = VolumeCSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data["csv_file"]
                overwrite = form.cleaned_data.get("overwrite", False)

                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.reader(decoded_file, delimiter="|")

                created_count, updated_count, skipped_count = 0, 0, 0
                for row in reader:
                    if len(row) < 3:
                        continue
                    volume_number, code, name = row[0], row[1], row[2]
                    subtitle = row[3] if len(row) > 3 else ""

                    if overwrite:
                        volume, created = Volume.objects.update_or_create(
                            code=code,
                            project=project,
                            defaults={
                                "name": name,
                                "subtitle": subtitle,
                            },
                        )
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    else:
                        volume, created = Volume.objects.get_or_create(
                            code=code,
                            project=project,
                            defaults={
                                "name": name,
                                "subtitle": subtitle,
                            },
                        )
                        if created:
                            created_count += 1
                        else:
                            skipped_count += 1

                if overwrite:
                    messages.success(request, f"Imported {created_count}, updated {updated_count} volumes.")
                else:
                    messages.success(request, f"Imported {created_count}, skipped {skipped_count} volumes.")

                return redirect(f"../../{project_id}/change/")
        else:
            form = VolumeCSVImportForm()

        context = {
            "form": form,
            "project": project,
            "opts": self.model._meta,
            "title": f"Import Volumes into {project.project_name}"
        }
        return render(request, "admin/provisioning/import_volumes.html", context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            "preview_marketplace_url": reverse("admin:provisioning_project_preview_marketplace", args=[object_id]),
            "preview_project_url": reverse("admin:provisioning_project_preview_project", args=[object_id]),
            "publish_staging_url": reverse("admin:provisioning_project_publish_staging", args=[object_id]),
            "import_volumes_url": reverse("admin:provisioning_project_import_volumes", args=[object_id]),
        })
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # --- JSON builders (unchanged) ---
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

    def preview_marketplace(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        return JsonResponse(self.build_marketplace_json(project), safe=False, json_dumps_params={"indent": 2})

    def preview_project(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        return JsonResponse(self.build_project_json(project), safe=False, json_dumps_params={"indent": 2})

    def publish_staging(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        project_json = self.build_project_json(project)
        marketplace_entry = self.build_marketplace_json(project)

        project_root = os.path.join(settings.PROJECT_ROOT, project.code, "metadata")
        os.makedirs(project_root, exist_ok=True)

        with open(os.path.join(project_root, "project.json"), "w", encoding="utf-8") as f:
            json.dump(project_json, f, indent=2, ensure_ascii=False)
        with open(os.path.join(project_root, "marketplace_snippet.json"), "w", encoding="utf-8") as f:
            json.dump(marketplace_entry, f, indent=2, ensure_ascii=False)

        messages.success(request, f"Published {project.code} metadata to staging.")
        return redirect(f"../../{project_id}/change/")


