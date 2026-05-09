from django.contrib import admin
from .models import Scholarship


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'level', 'deadline', 'is_active')
    list_filter = ('level', 'is_active')
    search_fields = ('title', 'provider', 'description')
