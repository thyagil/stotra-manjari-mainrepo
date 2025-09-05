from django.db import models
from django.core.exceptions import ValidationError
import os
from django.core.files.storage import FileSystemStorage


STATE_CHOICES = [
    (0, "Hidden"),
    (1, "Disabled"),
    (2, "Enabled"),
]

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        # If file exists, remove it before returning the name
        if self.exists(name):
            self.delete(name)
        return name

# ====================
# Artists
# ====================
class Artist(models.Model):
    id = models.AutoField(primary_key=True)
    artist_code = models.CharField(max_length=3, unique=True, blank=True, null=True,
                                   help_text="3-letter code, e.g. 'sgp' for Sriram Ghanapatigal")
    full_name = models.CharField(max_length=255, unique=True)
    formal_name = models.CharField(max_length=255, blank=True, null=True)
    short_bio = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)

    def clean(self):
        if len(self.artist_code) != 3:
            raise ValidationError({"artist_code": "Artist code must be exactly 3 characters"})
        if not self.artist_code.isalpha():
            raise ValidationError({"artist_code": "Artist code must contain only letters"})
        self.artist_code = self.artist_code.lower()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.formal_name or self.full_name


# ====================
# Categories (global)
# ====================
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.code})"


# ====================
# Languages (global)
# ====================
class Language(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.code})"


# ====================
# Projects
# ====================

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

    primary_artist = models.ForeignKey("Artist", on_delete=models.PROTECT, related_name="primary_projects")
    categories = models.ManyToManyField("Category", related_name="projects", blank=True)
    languages = models.ManyToManyField("Language", related_name="projects", blank=True)
    chapter_prefix = models.CharField(
        max_length=50,
        default="chapter_",
        help_text="Prefix to use when generating chapter codes (e.g., 'sarga_', 'adhyaya_').",
    )
    chapter_label = models.CharField(
        max_length=50,
        default="Chapter",
        help_text="Label used in chapter titles (e.g., 'Sarga', 'Adhyaya')."
    )

    cover_image = models.ImageField(
        upload_to=project_cover_path, storage=OverwriteStorage(), blank=True, null=True
    )
    banner_image = models.ImageField(
        upload_to=project_banner_path, storage=OverwriteStorage(), blank=True, null=True
    )

    def save(self, *args, **kwargs):
        if self.primary_artist and self.project_name:
            artist_code = self.primary_artist.artist_code.lower()
            project_slug = self.project_name.lower().replace(" ", "_")
            self.code = f"{artist_code}_{project_slug}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_name} ({self.code})"


# ====================
# Project Images
# ====================
class ProjectImage(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    key = models.CharField(max_length=50)   # "cover", "banner", etc.
    path = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.project.project_name} - {self.key}"


# ====================
# Contributors
# ====================
class Contributor(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="contributors")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="contributions")
    role = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.artist.full_name} - {self.role} ({self.project.project_name})"


# ====================
# Volumes
# ====================
def volume_thumbnail_path(instance, filename):
    project_code = instance.project.code
    volume_code = instance.code
    ext = filename.split(".")[-1].lower()
    return os.path.join(project_code, "images", volume_code, f"thumbnail.{ext}")

class Volume(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="volumes")
    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=volume_thumbnail_path, blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.project.project_name} - {self.name} ({self.code})"


# ====================
# Chapters
# ====================
class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="chapters", null=True, blank=True)
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, related_name="chapters", null=True, blank=True)

    index = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    state = models.IntegerField(default=2, choices=STATE_CHOICES)

    class Meta:
        ordering = ["index"]

    def __str__(self):
        parent = self.volume.name if self.volume else self.project.project_name
        return f"{parent} - {self.title or self.code}"
