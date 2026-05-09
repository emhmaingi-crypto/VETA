from django.contrib.auth.models import AbstractUser
from django.db import models


USER_TYPES = [
    ('student', 'Student/Graduate'),
    ('company', 'Company'),
    ('individual', 'Individual'),
]

LEVEL_CHOICES = [
    ('certificate', 'Certificate'),
    ('diploma', 'Diploma'),
    ('artisan', 'Artisan'),
    ('higher_diploma', 'Higher Diploma'),
]


class StudentUser(AbstractUser):
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')

    # Student fields
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    institution = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=150, blank=True)
    course = models.CharField(max_length=255, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True)
    graduation_year = models.PositiveSmallIntegerField(blank=True, null=True)
    skills = models.TextField(blank=True, help_text='Comma-separated skills')
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    projects = models.TextField(blank=True, help_text='Describe your projects and achievements')

    # Company/Individual fields
    company_name = models.CharField(max_length=255, blank=True)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)

    @property
    def profile_complete(self):
        if self.user_type == 'student':
            required = [
                self.first_name,
                self.last_name,
                self.email,
                self.institution,
                self.course,
                self.level,
                self.skills,
            ]
            return all(required)
        elif self.user_type in ['company', 'individual']:
            required = [
                self.first_name,
                self.last_name,
                self.email,
                self.company_name,
            ]
            return all(required)
        return False

    @property
    def display_name(self):
        if self.user_type == 'student':
            return f"{self.first_name} {self.last_name}"
        elif self.user_type == 'company':
            return self.company_name or f"{self.first_name} {self.last_name}"
        elif self.user_type == 'individual':
            return f"{self.first_name} {self.last_name}"
        return self.username

