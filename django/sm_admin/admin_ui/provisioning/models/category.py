from django.db import models

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.code})"
