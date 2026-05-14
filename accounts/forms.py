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
            'first_name', 'last_name', 'email',
            'profile_photo', 'phone_number', 'nationality', 'county',
            'bio',
            # student fields
            'institution', 'course', 'level', 'graduation_year',
            'id_number', 'languages',
            'skills', 'certifications', 'work_experience',
            'achievements', 'hobbies',
            'preferred_job_type', 'expected_salary',
            'projects', 'references',
            'linkedin_url', 'github_url', 'portfolio_url',
            'cv', 'is_available',
            # trainer fields
            'trainer_title', 'trainer_department',
            'trainer_expertise', 'trainer_years_experience',
            # company/individual fields
            'company_name', 'company_website', 'company_description',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.Textarea(attrs={'rows': 2}),
            'projects': forms.Textarea(attrs={'rows': 4}),
            'certifications': forms.Textarea(attrs={'rows': 3}),
            'work_experience': forms.Textarea(attrs={'rows': 4}),
            'achievements': forms.Textarea(attrs={'rows': 3}),
            'references': forms.Textarea(attrs={'rows': 3}),
            'trainer_expertise': forms.Textarea(attrs={'rows': 2}),
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }


class StudentLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Email address',
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'you@example.com'}),
    )

    def clean(self):
        identifier = self.cleaned_data.get('username', '').strip()
        from .models import StudentUser
        # Try matching by email (case-insensitive)
        user = StudentUser.objects.filter(email__iexact=identifier).first()
        if user:
            self.cleaned_data['username'] = user.username
        # If not found by email, leave as-is — Django will try it as a username
        return super().clean()
