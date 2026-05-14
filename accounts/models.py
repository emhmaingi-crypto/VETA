from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg


USER_TYPES = [
    ('student', 'Student/Graduate'),
    ('trainer', 'Trainer/Evaluator'),
    ('company', 'Company'),
    ('individual', 'Individual'),
]

LEVEL_CHOICES = [
    ('certificate', 'Certificate'),
    ('diploma', 'Diploma'),
    ('artisan', 'Artisan'),
    ('higher_diploma', 'Higher Diploma'),
]

BADGE_TYPES = [
    ('top_rated', 'Top Rated Trainee'),
    ('best_project', 'Best Project'),
    ('most_hired', 'Most Hired'),
    ('star_graduate', 'Star Graduate'),
    ('innovation', 'Innovation Award'),
]


class StudentUser(AbstractUser):
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')

    # Student/Trainee fields
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

    # Extended student fields
    phone_number = models.CharField(max_length=20, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    id_number = models.CharField(max_length=50, blank=True, help_text='National ID or student ID')
    languages = models.CharField(max_length=255, blank=True, help_text='Languages spoken, comma-separated')
    certifications = models.TextField(blank=True, help_text='List any certifications or short courses completed')
    work_experience = models.TextField(blank=True, help_text='Brief work or attachment experience')
    achievements = models.TextField(blank=True, help_text='Awards, competitions, or notable achievements')
    hobbies = models.CharField(max_length=255, blank=True)
    preferred_job_type = models.CharField(max_length=100, blank=True, help_text='e.g. Full-time, Part-time, Attachment')
    expected_salary = models.CharField(max_length=100, blank=True, help_text='Expected salary or rate range')
    references = models.TextField(blank=True, help_text='Name, title, and contact of a reference')

    # Trainer fields
    trainer_title = models.CharField(max_length=255, blank=True)
    trainer_department = models.CharField(max_length=255, blank=True)
    trainer_expertise = models.TextField(blank=True, help_text='Comma-separated expertise areas')
    trainer_years_experience = models.PositiveSmallIntegerField(blank=True, null=True)

    # Company/Individual fields
    company_name = models.CharField(max_length=255, blank=True)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)

    @property
    def is_trainer(self):
        return self.user_type == 'trainer'

    @property
    def average_rating(self):
        """Aggregate rating from service ratings + trainer evaluations."""
        from services.models import ServiceRating
        from projects.models import TrainerEvaluation
        service_avg = ServiceRating.objects.filter(
            application__freelancer=self
        ).aggregate(avg=Avg('rating'))['avg'] or 0
        eval_avg = TrainerEvaluation.objects.filter(
            trainee=self
        ).aggregate(avg=Avg('rating'))['avg'] or 0
        scores = [s for s in [service_avg, eval_avg] if s]
        return round(sum(scores) / len(scores), 1) if scores else 0

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
        elif self.user_type == 'trainer':
            required = [
                self.first_name,
                self.last_name,
                self.email,
                self.institution,
                self.trainer_title,
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

