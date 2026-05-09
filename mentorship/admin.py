from django.contrib import admin
from .models import Mentor, MentorshipRequest


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'organisation', 'slots_available', 'is_active')
    search_fields = ('name', 'expertise', 'organisation')
    list_filter = ('is_active',)


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'mentor', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('student__username', 'mentor__name')
