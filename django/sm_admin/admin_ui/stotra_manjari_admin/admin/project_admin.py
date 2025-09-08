import os, json, csv, subprocess
from pathlib import Path
from django import forms
from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.html import format_html
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.contrib.admin.sites import site
from django.test import RequestFactory

from ..orchestration.forms import AudioExtractionForm
from ..models import Project, Contributor, Volume
from ..models.orchestration import OrchestrationTask


# --- Inlines ---
class ContributorInline(admin.TabularInline):
    model = Contributor
    extra = 0
    classes = ("tab-contributors",)


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
        css = {"all": ("css/custom_admin.css",)}


class VolumeCSVImportForm(forms.Form):
    csv_file = forms.FileField()
    overwrite = forms.BooleanField(required=False, initial=False)


# --- Project Admin ---
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ("id", "project_name", "code", "format", "published", "featured")
    list_display_links = ("project_name",)
    list_filter = ("format", "published", "featured", "is_premium")
    search_fields = ("project_name", "code")

    readonly_fields = ("code", "code_with_button", "cover_preview", "banner_preview", "thumbnail_preview", "volumes_tab_content")

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
        ("Volumes", {"fields": (), "classes": ("tab-volumes",)}),
        ("Orchestration", {"fields": (), "classes": ("tab-orchestration",)}),
    )

    inlines = [ContributorInline]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        project = Project.objects.get(pk=object_id)

        extra_context.update({
            "import_volumes_url": reverse("admin:stotra_manjari_admin_project_import_volumes", args=[object_id]),
        })

        # tab persistence
        current_tab = request.GET.get("tab")
        if current_tab:
            extra_context["current_tab"] = current_tab


        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj:
            return fieldsets

        fs = []
        volume_id = request.GET.get("volume_id")

        for title, opts in fieldsets:
            if title == "Volumes":
                opts = dict(opts)
                if volume_id:
                    try:
                        volume = obj.volumes.get(pk=volume_id)
                    except Volume.DoesNotExist:
                        volume = None
                    html = self.render_volume_form(request, obj, volume)
                else:
                    html = render_to_string(
                        "admin/stotra_manjari_admin/project/volumes_list.html",
                        {"project": obj, "volumes": obj.volumes.all().order_by("code")},
                    )
                opts["description"] = mark_safe(html)
            fs.append((title, opts))
        return fs

    def volumes_tab_content(self, obj):
        if not obj:
            return "Save project first."

        # Build a fake request that hits Volume changelist, filtered by project
        rf = RequestFactory()
        request = rf.get(
            f"/admin/stotra_manjari_admin/volume/?project__id__exact={obj.id}"
        )
        request.user = getattr(self, "_current_request_user", None)

        # Find the registered VolumeAdmin
        volume_admin = site._registry[Volume]

        # Call its changelist_view
        response = volume_admin.changelist_view(request)

        # Render if it's a TemplateResponse
        if hasattr(response, "render") and callable(response.render):
            response = response.render()

        return mark_safe(response.content.decode("utf-8"))

    volumes_tab_content.short_description = ""  # hide label

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height: 75px;"/>', obj.thumbnail.url)
        return "No thumbnail"
    thumbnail_preview.short_description = "Thumbnail Preview"

    def render_volume_form(self, request, project, volume):
        from .volume_admin import ChapterInline, VolumeAdmin

        volume_admin = site._registry[Volume]
        form_class = volume_admin.get_form(request, obj=volume, change=True)
        form = form_class(instance=volume)

        # inline formset for chapters
        inline = ChapterInline(Volume, self.admin_site)
        formset_class = inline.get_formset(request, obj=volume, extra=0)
        formset = formset_class(instance=volume, queryset=volume.chapters.all())

        thumb_html = ""
        if volume and volume.thumbnail:
            thumb_html = f'<img src="{volume.thumbnail.url}" style="height:100px;">'

        context = {
            "project": project,
            "volume": volume,
            "form": form,
            "chapters_formset": formset,   # 👈 important
            "thumbnail_preview": mark_safe(thumb_html),
            "opts": volume._meta,
        }
        return render_to_string("admin/stotra_manjari_admin/project/volume_form.html", context)

    # --- Code field with Generate button ---
    def code_with_button(self, obj):
        if not obj or not obj.pk:
            return "Save project first to generate code."
        url = reverse("admin:stotra_manjari_admin_project_generate_code", args=[obj.pk])
        return format_html(
            '<div style="display:flex;align-items:center;gap:6px;">'
            '<input type="text" value="{}" readonly style="width:200px;"/>'
            '<a class="button" href="{}" title="Generate project code">⚙️</a>'
            '</div>',
            obj.code or "", url
        )
    code_with_button.short_description = "Project Code"

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
        return redirect(reverse("admin:stotra_manjari_admin_project_change", args=[project_id]))

    def response_change(self, request, obj):
        res = super().response_change(request, obj)
        if isinstance(res, HttpResponseRedirect) and "volume_id" in request.GET:
            res["Location"] += "#volumes-tab"
        return res

    # --- Image previews ---
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="height:100px;"/>', obj.cover_image.url)
        return ""
    cover_preview.short_description = "Cover Preview"

    def banner_preview(self, obj):
        if obj.banner_image:
            return format_html('<img src="{}" style="height:100px;"/>', obj.banner_image.url)
        return ""
    banner_preview.short_description = "Banner Preview"

    # --- Custom URLs ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:project_id>/generate_code/", self.admin_site.admin_view(self.generate_code_view),
                 name="stotra_manjari_admin_project_generate_code"),
            path("<int:project_id>/import_volumes/", self.admin_site.admin_view(self.import_volumes_view),
                 name="stotra_manjari_admin_project_import_volumes"),
            path(
                "<int:project_id>/volumes/",
                self.admin_site.admin_view(self.volumes_list_view),
                name="stotra_manjari_admin_project_volumes",
            ),
            path("<int:project_id>/volumes/<int:volume_id>/", self.admin_site.admin_view(self.volume_detail_view),
                 name="stotra_manjari_admin_project_volume_detail"),
        ]
        return custom_urls + urls

    def volumes_list_view(self, request, project_id):
        return redirect(
            f"/admin/stotra_manjari_admin/project/{project_id}/change/?tab=volumes#volumes-tab"
        )

    def volume_detail_view(self, request, project_id, volume_id):
        return redirect(
            f"/admin/stotra_manjari_admin/project/{project_id}/change/?tab=volumes&volume_id={volume_id}#volumes-tab"
        )

    # --- Import volumes ---
    def import_volumes_view(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        if request.method == "POST":
            form = VolumeCSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data["csv_file"]
                overwrite = form.cleaned_data.get("overwrite", False)
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.reader(decoded_file, delimiter="|")

                created, updated, skipped = 0, 0, 0
                for row in reader:
                    if len(row) < 3: continue
                    _, code, name = row[:3]
                    subtitle = row[3] if len(row) > 3 else ""
                    if overwrite:
                        _, created_flag = Volume.objects.update_or_create(
                            code=code, project=project,
                            defaults={"name": name, "subtitle": subtitle},
                        )
                        if created_flag: created += 1
                        else: updated += 1
                    else:
                        _, created_flag = Volume.objects.get_or_create(
                            code=code, project=project,
                            defaults={"name": name, "subtitle": subtitle},
                        )
                        if created_flag: created += 1
                        else: skipped += 1

                messages.success(
                    request,
                    f"Imported {created}, updated {updated}, skipped {skipped} volumes."
                )
                return redirect(f"../../{project_id}/change/")
        else:
            form = VolumeCSVImportForm()
        return render(request, "admin/stotra_manjari_admin/import_volumes.html", {
            "form": form, "project": project, "opts": self.model._meta,
            "title": f"Import Volumes into {project.project_name}"
        })
