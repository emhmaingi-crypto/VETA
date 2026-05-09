from django.db import models
from django.urls import reverse
from django.utils import timezone


OPPORTUNITY_TYPES = [
    ('job', 'Job'),
    ('internship', 'Internship'),
    ('attachment', 'Attachment'),
    ('apprenticeship', 'Apprenticeship'),
    ('volunteer', 'Volunteer'),
]

LEVEL_CHOICES = [
    ('certificate', 'Certificate'),
    ('diploma', 'Diploma'),
    ('artisan', 'Artisan'),
    ('higher_diploma', 'Higher Diploma'),
]


class PartnerOrganisation(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=120, blank=True)
    logo = models.ImageField(upload_to='partners/', blank=True, null=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    county = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Opportunity(models.Model):
    partner = models.ForeignKey(PartnerOrganisation, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=OPPORTUNITY_TYPES)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    skills_required = models.TextField(blank=True, help_text='Comma-separated skills')
    level_required = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True)
    county = models.CharField(max_length=100, blank=True)
    stipend = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=120, blank=True)
    deadline = models.DateField(default=timezone.now)
    slots = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('opportunities:detail', args=[str(self.pk)])


APPLICATION_STATUS = [
    ('pending', 'Pending'),
    ('reviewing', 'Reviewing'),
    ('shortlisted', 'Shortlisted'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]


class Application(models.Model):
    student = models.ForeignKey('accounts.StudentUser', on_delete=models.CASCADE, related_name='applications')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    ai_match_score = models.PositiveSmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'opportunity')

    def __str__(self):
        return f'{self.student.username} → {self.opportunity.title}'
