import io
import qrcode

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic
from opportunities.models import Application, Opportunity
from mentorship.models import MentorshipRequest
from scholarships.models import Scholarship
from services.models import ServiceApplication
from projects.models import Project, TrainerEvaluation, RecognitionBadge
from .forms import StudentLoginForm, StudentProfileForm, StudentRegisterForm
from .models import StudentUser


class RegisterView(generic.CreateView):
    model = StudentUser
    form_class = StudentRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Welcome to VETA Connect. Your profile is ready to update.')
        return response


def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


class ProfileEditView(LoginRequiredMixin, generic.UpdateView):
    model = StudentUser
    form_class = StudentProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.user_type == 'student':
            context['applications'] = Application.objects.filter(student=user).order_by('-created_at')[:5]
            context['requests'] = MentorshipRequest.objects.filter(student=user).order_by('-created_at')[:5]
            context['scholarships'] = Scholarship.objects.filter(is_active=True)[:4]
            context['matched_opportunities'] = Opportunity.objects.filter(is_active=True)[:4]
            context['service_applications'] = ServiceApplication.objects.filter(freelancer=user).select_related('listing')[:5]
            context['my_projects'] = Project.objects.filter(trainee=user).order_by('-created_at')[:5]
            context['my_badges'] = RecognitionBadge.objects.filter(trainee=user).order_by('-awarded_at')[:6]
            context['my_evaluations'] = TrainerEvaluation.objects.filter(trainee=user).select_related('trainer').order_by('-created_at')[:5]
            context['avg_rating'] = user.average_rating
        elif user.user_type == 'trainer':
            context['recent_evaluations'] = TrainerEvaluation.objects.filter(trainer=user).select_related('trainee', 'project').order_by('-created_at')[:8]
            context['badges_awarded'] = RecognitionBadge.objects.filter(awarded_by=user).select_related('trainee').order_by('-awarded_at')[:6]
            context['pending_projects'] = Project.objects.filter(is_public=True).order_by('-created_at')[:6]
        context['profile_complete'] = user.profile_complete
        return context


def public_profile_view(request, username):
    """Publicly accessible profile page — used as the QR code landing page."""
    profile_user = get_object_or_404(StudentUser, username=username)
    return render(request, 'accounts/public_profile.html', {'profile_user': profile_user})


def profile_qr_view(request, username):
    """Return a QR code PNG that encodes the user's public profile URL."""
    get_object_or_404(StudentUser, username=username)
    profile_url = request.build_absolute_uri(
        reverse_lazy('accounts:public_profile', kwargs={'username': username})
    )
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(profile_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')


def qr_print_view(request, username):
    """Render a print-friendly QR card page."""
    profile_user = get_object_or_404(StudentUser, username=username)
    public_profile_url = request.build_absolute_uri(
        reverse_lazy('accounts:public_profile', kwargs={'username': username})
    )
    qr_image_url = request.build_absolute_uri(
        reverse_lazy('accounts:profile_qr', kwargs={'username': username})
    )
    return render(request, 'accounts/qr_print.html', {
        'profile_user': profile_user,
        'public_profile_url': public_profile_url,
        'profile_url': qr_image_url,
    })
