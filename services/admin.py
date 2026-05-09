from django.contrib import admin
from .models import ServiceApplication, ServiceListing, ServiceRating


@admin.register(ServiceListing)
class ServiceListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_name', 'category', 'deadline', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'client_name', 'description', 'skills_required')
    readonly_fields = ('created_at',)
    actions = ['mark_active', 'mark_inactive']

    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} service listings marked as active.")
    mark_active.short_description = "Mark selected service listings as active"

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} service listings marked as inactive.")
    mark_inactive.short_description = "Mark selected service listings as inactive"


@admin.register(ServiceApplication)
class ServiceApplicationAdmin(admin.ModelAdmin):
    list_display = ('freelancer', 'listing', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('freelancer__username', 'listing__title')
    readonly_fields = ('created_at',)
    actions = ['mark_pending', 'mark_reviewing', 'mark_accepted', 'mark_completed', 'mark_rejected']

    def mark_pending(self, request, queryset):
        queryset.update(status='pending')
        self.message_user(request, f"{queryset.count()} applications marked as pending.")
    mark_pending.short_description = "Mark selected applications as pending"

    def mark_reviewing(self, request, queryset):
        queryset.update(status='reviewing')
        self.message_user(request, f"{queryset.count()} applications marked as reviewing.")
    mark_reviewing.short_description = "Mark selected applications as reviewing"

    def mark_accepted(self, request, queryset):
        queryset.update(status='accepted')
        self.message_user(request, f"{queryset.count()} applications marked as accepted.")
    mark_accepted.short_description = "Mark selected applications as accepted"

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} applications marked as completed.")
    mark_completed.short_description = "Mark selected applications as completed"

    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} applications marked as rejected.")
    mark_rejected.short_description = "Mark selected applications as rejected"


@admin.register(ServiceRating)
class ServiceRatingAdmin(admin.ModelAdmin):
    list_display = ('application', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('application__freelancer__username', 'application__listing__title')
