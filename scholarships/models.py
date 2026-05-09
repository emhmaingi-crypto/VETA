from django.db import models
from django.urls import reverse


LEVEL_CHOICES = [
    ('certificate', 'Certificate'),
    ('diploma', 'Diploma'),
    ('artisan', 'Artisan'),
    ('higher_diploma', 'Higher Diploma'),
]


class Scholarship(models.Model):
    title = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='scholarships/', blank=True, null=True)
    description = models.TextField()
    eligibility = models.TextField(blank=True)
    amount = models.CharField(max_length=120, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True)
    deadline = models.DateField(blank=True, null=True)
    apply_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('scholarships:detail', args=[str(self.pk)])
