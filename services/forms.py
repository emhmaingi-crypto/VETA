from django import forms
from .models import ServiceApplication, ServiceRating


class AISupportForm(forms.Form):
    issue_description = forms.CharField(
        label='Describe your technical issue',
        widget=forms.Textarea(
            attrs={
                'rows': 6,
                'placeholder': 'Explain your issue, for example: "My campus Wi-Fi won\'t connect after I changed the router settings."',
            }
        ),
        help_text='Ask about network configuration, system setup, device troubleshooting, or user support tasks.',
    )


class ServiceApplicationForm(forms.ModelForm):
    class Meta:
        model = ServiceApplication
        fields = ['proposal', 'expected_price']
        widgets = {
            'proposal': forms.Textarea(attrs={'rows': 6}),
            'expected_price': forms.TextInput(attrs={'placeholder': 'Reasonable budget or rate'}),
        }


class ServiceRatingForm(forms.ModelForm):
    class Meta:
        model = ServiceRating
        fields = ['rating', 'review']
        widgets = {
            'review': forms.Textarea(attrs={'rows': 4}),
        }
