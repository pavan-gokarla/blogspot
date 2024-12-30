from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Media)
admin.site.register(Blog)
admin.site.register(CodeSnippets)
admin.site.register(Comment)
admin.site.register(Tags)