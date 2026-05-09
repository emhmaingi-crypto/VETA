from django.contrib import admin
from .models import Application, Opportunity, PartnerOrganisation


@admin.register(PartnerOrganisation)
class PartnerOrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'county', 'is_verified')
    search_fields = ('name', 'type', 'county')


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'partner', 'type', 'level_required', 'county', 'deadline', 'is_active', 'created_at')
    list_filter = ('type', 'level_required', 'county', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'requirements', 'skills_required')
    readonly_fields = ('created_at',)
    actions = ['mark_active', 'mark_inactive']

    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} opportunities marked as active.")
    mark_active.short_description = "Mark selected opportunities as active"

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} opportunities marked as inactive.")
    mark_inactive.short_description = "Mark selected opportunities as inactive"


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'status', 'created_at', 'ai_match_score')
    list_filter = ('status', 'created_at')
    search_fields = ('student__username', 'opportunity__title')
    readonly_fields = ('created_at',)
    actions = ['mark_pending', 'mark_reviewing', 'mark_shortlisted', 'mark_accepted', 'mark_rejected']

    def mark_pending(self, request, queryset):
        queryset.update(status='pending')
        self.message_user(request, f"{queryset.count()} applications marked as pending.")
    mark_pending.short_description = "Mark selected applications as pending"

    def mark_reviewing(self, request, queryset):
        queryset.update(status='reviewing')
        self.message_user(request, f"{queryset.count()} applications marked as reviewing.")
    mark_reviewing.short_description = "Mark selected applications as reviewing"

    def mark_shortlisted(self, request, queryset):
        queryset.update(status='shortlisted')
        self.message_user(request, f"{queryset.count()} applications marked as shortlisted.")
    mark_shortlisted.short_description = "Mark selected applications as shortlisted"

    def mark_accepted(self, request, queryset):
        queryset.update(status='accepted')
        self.message_user(request, f"{queryset.count()} applications marked as accepted.")
    mark_accepted.short_description = "Mark selected applications as accepted"

    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} applications marked as rejected.")
    mark_rejected.short_description = "Mark selected applications as rejected"
