from django.contrib import admin
from .models import Project, ProjectImage, TrainerEvaluation, RecognitionBadge


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'trainee', 'course_area', 'status', 'is_public', 'created_at']
    list_filter = ['course_area', 'status', 'is_public']
    search_fields = ['title', 'trainee__username', 'trainee__first_name', 'trainee__last_name']
    inlines = [ProjectImageInline]


@admin.register(TrainerEvaluation)
class TrainerEvaluationAdmin(admin.ModelAdmin):
    list_display = ['trainee', 'trainer', 'project', 'rating', 'recommended_for_freelance', 'created_at']
    list_filter = ['rating', 'recommended_for_freelance', 'recommended_for_mentorship']
    search_fields = ['trainee__username', 'trainer__username']


@admin.register(RecognitionBadge)
class RecognitionBadgeAdmin(admin.ModelAdmin):
    list_display = ['trainee', 'badge_type', 'title', 'awarded_by', 'awarded_at']
    list_filter = ['badge_type']
    search_fields = ['trainee__username', 'title']
