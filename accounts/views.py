import io
import json
import qrcode

from anthropic import Anthropic
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from opportunities.models import Application, Opportunity
from mentorship.models import MentorshipRequest
from scholarships.models import Scholarship
from services.models import ServiceApplication
from projects.models import Project, TrainerEvaluation, RecognitionBadge
from .forms import StudentLoginForm, StudentProfileForm, StudentRegisterForm

# Re-export StudentLoginForm so urls.py can import it from views
__all__ = ['StudentLoginForm']
from .models import StudentUser


class RegisterView(generic.CreateView):
    model = StudentUser
    form_class = StudentRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:dashboard')

    def form_valid(self, form):
        # Auto-generate a unique username from the email (before the @)
        import re
        user = form.save(commit=False)
        base = re.sub(r'[^a-zA-Z0-9]', '', user.email.split('@')[0])[:20] or 'user'
        username = base
        counter = 1
        while StudentUser.objects.filter(username=username).exists():
            username = f'{base}{counter}'
            counter += 1
        user.username = username
        user.save()
        login(self.request, user)
        messages.success(self.request, 'Welcome to VETA Connect. Your profile is ready to update.')
        return redirect(self.success_url)


@login_required
def profile_view(request):
    user = request.user
    ctx = {'user': user}
    if user.user_type == 'student':
        ctx['my_projects'] = Project.objects.filter(trainee=user).order_by('-created_at')[:6]
        ctx['my_badges'] = RecognitionBadge.objects.filter(trainee=user).order_by('-awarded_at')
        ctx['my_evaluations'] = TrainerEvaluation.objects.filter(trainee=user).select_related('trainer', 'project').order_by('-created_at')[:5]
        ctx['service_apps'] = ServiceApplication.objects.filter(freelancer=user).select_related('listing').order_by('-created_at')[:5]
        ctx['opp_apps'] = Application.objects.filter(student=user).select_related('opportunity').order_by('-created_at')[:5]
        ctx['avg_rating'] = user.average_rating
    elif user.user_type == 'trainer':
        ctx['evaluated_count'] = TrainerEvaluation.objects.filter(trainer=user).count()
        ctx['badges_awarded'] = RecognitionBadge.objects.filter(awarded_by=user).select_related('trainee').order_by('-awarded_at')[:8]
        ctx['recent_evaluations'] = TrainerEvaluation.objects.filter(trainer=user).select_related('trainee', 'project').order_by('-created_at')[:5]
    ctx['profile_complete'] = user.profile_complete
    return render(request, 'accounts/profile.html', ctx)


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


# ── AI Profile Assistant ──────────────────────────────────────────────────────

# Map of editable field names to human-readable labels
_AI_FIELDS = {
    'bio': 'Bio / About me',
    'skills': 'Skills (comma-separated)',
    'projects': 'Projects & achievements',
    'certifications': 'Certifications & short courses',
    'work_experience': 'Work / attachment experience',
    'achievements': 'Awards and notable achievements',
    'company_description': 'Company / Organisation description',
    'trainer_expertise': 'Trainer expertise areas',
}

# System prompt shared by all field assists
_AI_SYSTEM = (
    'You are an expert TVET career coach helping students, trainers, and companies '
    'write compelling, professional profile content for a digital platform called VETA Connect. '
    'Write concise, natural text suitable for the requested profile field. '
    'Return ONLY the text for that field — no preamble, no quotation marks, no labels.'
)


@login_required
@require_POST
def profile_ai_assist(request):
    """AJAX endpoint: given a field name and user prompt, return AI-generated text."""
    ai_key = settings.ANTHROPIC_API_KEY
    if not ai_key:
        return JsonResponse({'error': 'AI is not configured on this server.'}, status=503)

    field = request.POST.get('field', '').strip()
    user_prompt = request.POST.get('prompt', '').strip()

    if field not in _AI_FIELDS:
        return JsonResponse({'error': 'Invalid field.'}, status=400)
    if not user_prompt:
        return JsonResponse({'error': 'Please describe what you want the AI to write.'}, status=400)

    user = request.user
    context_lines = [
        f"Name: {user.get_full_name() or user.username}",
        f"Role: {user.get_user_type_display()}",
    ]
    if user.institution:
        context_lines.append(f"Institution: {user.institution}")
    if user.course:
        context_lines.append(f"Course: {user.course}")
    if user.level:
        context_lines.append(f"Level: {user.get_level_display()}")
    if user.skills:
        context_lines.append(f"Existing skills: {user.skills}")

    full_prompt = (
        f"Profile context:\n{chr(10).join(context_lines)}\n\n"
        f"Field to write: {_AI_FIELDS[field]}\n\n"
        f"User instruction: {user_prompt}"
    )

    try:
        client = Anthropic(api_key=ai_key)
        response = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=500,
            system=_AI_SYSTEM,
            messages=[{'role': 'user', 'content': full_prompt}],
        )
        result = response.content[0].text.strip()
        return JsonResponse({'result': result})
    except Exception as exc:
        return JsonResponse({'error': f'AI unavailable: {exc}'}, status=503)
