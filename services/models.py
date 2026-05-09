from django.db import models
from django.urls import reverse
from django.utils import timezone

SERVICE_CATEGORIES = [
    ('digital', 'Digital services'),
    ('creative', 'Creative & design'),
    ('technical', 'Technical support'),
    ('business', 'Business & administration'),
    ('training', 'Training & coaching'),
]

APPLICATION_STATUS = [
    ('pending', 'Pending'),
    ('reviewing', 'Reviewing'),
    ('accepted', 'Accepted'),
    ('completed', 'Completed'),
    ('rejected', 'Rejected'),
]


class ServiceListing(models.Model):
    client_name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=SERVICE_CATEGORIES, blank=True)
    description = models.TextField()
    skills_required = models.TextField(blank=True, help_text='Comma-separated skills')
    budget_range = models.CharField(max_length=120, blank=True)
    timeline = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    deadline = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-deadline', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('services:detail', args=[str(self.pk)])


class ServiceApplication(models.Model):
    freelancer = models.ForeignKey('accounts.StudentUser', on_delete=models.CASCADE, related_name='service_applications')
    listing = models.ForeignKey(ServiceListing, on_delete=models.CASCADE, related_name='applications')
    proposal = models.TextField()
    expected_price = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('freelancer', 'listing')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.freelancer.username} → {self.listing.title}'


class ServiceRating(models.Model):
    application = models.OneToOneField(ServiceApplication, on_delete=models.CASCADE, related_name='rating')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Rating for {self.application}'
