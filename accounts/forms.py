from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import StudentUser, USER_TYPES


class StudentRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(choices=USER_TYPES, widget=forms.RadioSelect, initial='student')

    class Meta:
        model = StudentUser
        fields = ['username', 'first_name', 'last_name', 'email', 'user_type', 'password1', 'password2']


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'bio',
            'profile_photo',
            'institution',
            'county',
            'course',
            'level',
            'graduation_year',
            'skills',
            'projects',
            'linkedin_url',
            'github_url',
            'portfolio_url',
            'cv',
            'is_available',
            # trainer fields
            'trainer_title',
            'trainer_department',
            'trainer_expertise',
            'trainer_years_experience',
            # company/individual fields
            'company_name',
            'company_website',
            'company_description',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.Textarea(attrs={'rows': 2}),
            'projects': forms.Textarea(attrs={'rows': 4}),
            'trainer_expertise': forms.Textarea(attrs={'rows': 2}),
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }


class StudentLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
