from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic
from opportunities.models import Application, Opportunity
from mentorship.models import MentorshipRequest
from scholarships.models import Scholarship
from services.models import ServiceApplication
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
        context['applications'] = Application.objects.filter(student=user).order_by('-created_at')[:5]
        context['requests'] = MentorshipRequest.objects.filter(student=user).order_by('-created_at')[:5]
        context['scholarships'] = Scholarship.objects.filter(is_active=True)[:4]
        context['matched_opportunities'] = Opportunity.objects.filter(is_active=True)[:4]
        context['service_applications'] = ServiceApplication.objects.filter(freelancer=user).select_related('listing')[:5]
        context['profile_complete'] = user.profile_complete
        return context
