# Branding
from django.contrib import admin

admin.site.site_header = "Stotra Manjari Admin"
admin.site.site_title = "Stotra Manjari Admin"
admin.site.index_title = "Welcome to Stotra Manjari Admin"

# Pull in all admin modules
from .project_admin import *
from .volume_admin import *
from .chapter_admin import *
from .artist_admin import *
from .category_admin import *
from .language_admin import *
