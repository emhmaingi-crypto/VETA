from django import forms
from .models import Application, Opportunity


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 6}),
        }


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            'title',
            'type',
            'description',
            'requirements',
            'skills_required',
            'level_required',
            'county',
            'stipend',
            'duration',
            'deadline',
            'slots',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'skills_required': forms.Textarea(attrs={'rows': 2}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
