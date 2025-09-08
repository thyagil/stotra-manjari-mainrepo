from django.db import models
from django.core.exceptions import ValidationError

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
