from django import forms
from .models import MentorshipRequest


class MentorshipRequestForm(forms.ModelForm):
    class Meta:
        model = MentorshipRequest
        fields = ['message', 'goals']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
            'goals': forms.Textarea(attrs={'rows': 4}),
        }
