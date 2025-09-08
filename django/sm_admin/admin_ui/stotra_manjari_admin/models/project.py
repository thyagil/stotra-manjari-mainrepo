import os
from django.db import models
from .base import OverwriteStorage
from .artist import Artist
from .category import Category
from .language import Language

def project_cover_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return os.path.join(instance.code, "images", "project", f"cover{ext}")

def project_banner_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return os.path.join(instance.code, "images", "project", f"banner{ext}")


class Project(models.Model):
    TYPE_CHOICES = [
        ("audio_book", "Audio Book"),
        ("e_book", "E-Book"),
        ("music_album", "Music Album"),
    ]
    FORMAT_CHOICES = [
        ("volume", "Volume-based"),
        ("chapter", "Chapter-based"),
        ("standalone", "Standalone"),
    ]

    class Meta:
        app_label = "stotra_manjari_admin"

    @property
    def metadata_is_valid(self):
        # 🔹 Replace with real validation later
        # return bool(self.code and self.volumes.exists())
        return True

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    project_name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    description = models.TextField(blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    preview = models.TextField(blank=True, null=True)

    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    currency = models.CharField(max_length=10, default="USD")
    price = models.FloatField(default=0.0)

    primary_artist = models.ForeignKey(Artist, on_delete=models.PROTECT, related_name="primary_projects")
    categories = models.ManyToManyField(Category, related_name="projects", blank=True)
    languages = models.ManyToManyField(Language, related_name="projects", blank=True)
    chapter_prefix = models.CharField(max_length=50, default="chapter_")
    chapter_label = models.CharField(max_length=50, default="Chapter")

    cover_image = models.ImageField(upload_to=project_cover_path, storage=OverwriteStorage(), blank=True, null=True)
    banner_image = models.ImageField(upload_to=project_banner_path, storage=OverwriteStorage(), blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.primary_artist and self.project_name:
            artist_code = self.primary_artist.artist_code.lower()
            project_slug = self.project_name.lower().replace(" ", "_")
            self.code = f"{artist_code}_{project_slug}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_name} ({self.code})"
