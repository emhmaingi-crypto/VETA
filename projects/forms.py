from django import forms
from .models import Project, ProjectImage, TrainerEvaluation, RecognitionBadge


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'course_area',
            'technologies',
            'status',
            'is_public',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'id': 'id_description'}),
            'technologies': forms.TextInput(attrs={'placeholder': 'e.g. Arduino, Python, Welding, AutoCAD'}),
        }


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Brief description of this image'}),
        }


ProjectImageFormSet = forms.inlineformset_factory(
    Project,
    ProjectImage,
    form=ProjectImageForm,
    extra=3,
    max_num=10,
    can_delete=True,
)


class TrainerEvaluationForm(forms.ModelForm):
    class Meta:
        model = TrainerEvaluation
        fields = [
            'rating',
            'practical_skills',
            'theoretical_knowledge',
            'creativity',
            'professionalism',
            'feedback',
            'strengths',
            'areas_for_improvement',
            'recommended_for_freelance',
            'recommended_for_mentorship',
        ]
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Detailed feedback and guidance…'}),
            'strengths': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What the trainee does well…'}),
            'areas_for_improvement': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Areas that need more work…'}),
        }
        labels = {
            'rating': 'Overall Rating',
            'practical_skills': 'Practical Skills',
            'theoretical_knowledge': 'Theoretical Knowledge',
            'creativity': 'Creativity & Innovation',
            'professionalism': 'Professionalism & Attitude',
        }


class AwardBadgeForm(forms.ModelForm):
    class Meta:
        model = RecognitionBadge
        fields = ['badge_type', 'title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
