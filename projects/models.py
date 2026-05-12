from django.db import models
from django.urls import reverse
from django.db.models import Avg


COURSE_AREAS = [
    ('engineering', 'Engineering & Technology'),
    ('ict', 'ICT & Computing'),
    ('construction', 'Building & Construction'),
    ('automotive', 'Automotive & Transport'),
    ('electrical', 'Electrical & Electronics'),
    ('hospitality', 'Hospitality & Tourism'),
    ('agriculture', 'Agriculture & Food'),
    ('health', 'Health & Social Care'),
    ('business', 'Business & Commerce'),
    ('creative', 'Creative Arts & Fashion'),
    ('other', 'Other'),
]

PROJECT_STATUS = [
    ('concept', 'Concept / Idea'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('deployed', 'Deployed / In Use'),
]

EVAL_CRITERIA = [
    (1, '1 - Needs significant improvement'),
    (2, '2 - Below expectations'),
    (3, '3 - Meets expectations'),
    (4, '4 - Exceeds expectations'),
    (5, '5 - Outstanding'),
]


class Project(models.Model):
    trainee = models.ForeignKey(
        'accounts.StudentUser',
        on_delete=models.CASCADE,
        related_name='showcase_projects',
        limit_choices_to={'user_type': 'student'},
    )
    title = models.CharField(max_length=255)
    description = models.TextField(help_text='Describe your project in detail.')
    ai_summary = models.TextField(
        blank=True,
        help_text='AI-generated concise summary of the project.',
    )
    ai_expanded = models.TextField(
        blank=True,
        help_text='AI-expanded detailed write-up of the project.',
    )
    course_area = models.CharField(max_length=50, choices=COURSE_AREAS, default='other')
    technologies = models.TextField(
        blank=True,
        help_text='Comma-separated tools, materials, or technologies used.',
    )
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='completed')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.trainee.get_full_name()}'

    def get_absolute_url(self):
        return reverse('projects:detail', args=[self.pk])

    @property
    def average_rating(self):
        result = self.evaluations.aggregate(avg=Avg('rating'))['avg']
        return round(result, 1) if result else None

    @property
    def cover_image(self):
        img = self.images.first()
        return img.image if img else None


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='project_images/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f'Image for {self.project.title}'


class TrainerEvaluation(models.Model):
    trainer = models.ForeignKey(
        'accounts.StudentUser',
        on_delete=models.CASCADE,
        related_name='evaluations_given',
        limit_choices_to={'user_type': 'trainer'},
    )
    trainee = models.ForeignKey(
        'accounts.StudentUser',
        on_delete=models.CASCADE,
        related_name='evaluations_received',
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='evaluations',
        blank=True,
        null=True,
    )
    rating = models.PositiveSmallIntegerField(choices=EVAL_CRITERIA)
    practical_skills = models.PositiveSmallIntegerField(choices=EVAL_CRITERIA, default=3)
    theoretical_knowledge = models.PositiveSmallIntegerField(choices=EVAL_CRITERIA, default=3)
    creativity = models.PositiveSmallIntegerField(choices=EVAL_CRITERIA, default=3)
    professionalism = models.PositiveSmallIntegerField(choices=EVAL_CRITERIA, default=3)
    feedback = models.TextField(help_text='Detailed feedback and guidance for the trainee.')
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    recommended_for_freelance = models.BooleanField(default=False)
    recommended_for_mentorship = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.trainer.get_full_name()} evaluated {self.trainee.get_full_name()}'


class RecognitionBadge(models.Model):
    trainee = models.ForeignKey(
        'accounts.StudentUser',
        on_delete=models.CASCADE,
        related_name='badges',
    )
    badge_type = models.CharField(max_length=30, choices=[
        ('top_rated', 'Top Rated Trainee'),
        ('best_project', 'Best Project'),
        ('most_hired', 'Most Hired'),
        ('star_graduate', 'Star Graduate'),
        ('innovation', 'Innovation Award'),
        ('trainer_pick', "Trainer's Pick"),
    ])
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    awarded_by = models.ForeignKey(
        'accounts.StudentUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='badges_awarded',
    )
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-awarded_at']

    def __str__(self):
        return f'{self.badge_type} → {self.trainee.get_full_name()}'
