from django.db import models


class Mentor(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True)
    organisation = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='mentors/', blank=True, null=True)
    bio = models.TextField(blank=True)
    expertise = models.TextField(blank=True, help_text='Comma-separated expertise areas')
    email = models.EmailField(blank=True)
    linkedin_url = models.URLField(blank=True)
    slots_available = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


REQUEST_STATUS = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('declined', 'Declined'),
    ('completed', 'Completed'),
]


class MentorshipRequest(models.Model):
    student = models.ForeignKey('accounts.StudentUser', on_delete=models.CASCADE, related_name='mentorship_requests')
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='requests')
    message = models.TextField()
    goals = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.username} → {self.mentor.name}'
