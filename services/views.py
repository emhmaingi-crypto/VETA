import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from anthropic import Anthropic

from .forms import AISupportForm, ServiceApplicationForm
from .models import ServiceApplication, ServiceListing


class ServiceListView(generic.ListView):
    model = ServiceListing
    template_name = 'services/list.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        queryset = ServiceListing.objects.filter(is_active=True)
        query = self.request.GET.get('q', '')
        category = self.request.GET.get('category', '')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(skills_required__icontains=query)
            )
        if category:
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceListing._meta.get_field('category').choices
        context['query'] = self.request.GET.get('q', '')
        context['category'] = self.request.GET.get('category', '')
        return context


class AISupportView(LoginRequiredMixin, generic.FormView):
    template_name = 'services/ai_support.html'
    form_class = AISupportForm

    def get_initial(self):
        initial = super().get_initial()
        issue_description = self.request.GET.get('issue_description', '')
        if issue_description:
            initial['issue_description'] = issue_description
        return initial

    def form_valid(self, form):
        issue_description = form.cleaned_data['issue_description']
        ai_key = settings.ANTHROPIC_API_KEY
        context = self.get_context_data(form=form)
        context['issue_description'] = issue_description

        if not ai_key:
            context['error'] = 'AI support is not configured. Add ANTHROPIC_API_KEY to your environment.'
            return self.render_to_response(context)

        try:
            client = Anthropic(api_key=ai_key)
            response = client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=700,
                temperature=0.2,
                messages=[
                    {
                        'role': 'user',
                        'content': self.build_prompt(self.request.user, issue_description),
                    }
                ],
            )
            context['support_response'] = self.parse_response(response)
        except json.JSONDecodeError:
            context['error'] = 'AI support returned an unexpected format. Please try again later.'
        except Exception:
            context['error'] = 'AI support is unavailable right now. Please try later.'

        return self.render_to_response(context)

    def parse_response(self, response):
        if not getattr(response, 'content', None):
            return ''

        try:
            return response.content[0].text.strip()
        except (IndexError, AttributeError):
            return ''

    def build_prompt(self, user, issue_description):
        profile = (
            f"Student name: {user.get_full_name()}\n"
            f"Course: {user.course or 'N/A'}\n"
            f"Level: {user.level or 'N/A'}\n"
            f"Skills: {user.skills or 'N/A'}\n"
            f"Bio: {user.bio or 'N/A'}\n"
        )

        prompt = (
            'You are an expert TVET IT support engineer. The student needs practical troubleshooting guidance for a technical support issue. '
            'Provide a clear diagnosis, step-by-step troubleshooting actions, and any configuration commands or checks the student should use. '
            'Keep the response relevant to vocational technical support and user support scenarios.\n\n'
            'Student profile:\n'
            f'{profile}\n'
            'Issue description:\n'
            f'{issue_description}\n\n'
            'Answer in plain text with numbered steps and include the likely cause where appropriate.'
        )

        return prompt


class ServiceDetailView(generic.DetailView):
    model = ServiceListing
    template_name = 'services/detail.html'
    context_object_name = 'service'


class ServiceApplyView(LoginRequiredMixin, generic.CreateView):
    model = ServiceApplication
    form_class = ServiceApplicationForm
    template_name = 'services/apply.html'

    def dispatch(self, request, *args, **kwargs):
        self.service = get_object_or_404(ServiceListing, pk=kwargs['pk'], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        application = form.save(commit=False)
        application.freelancer = self.request.user
        application.listing = self.service
        try:
            application.save()
        except IntegrityError:
            messages.warning(self.request, 'You have already submitted a proposal for this service.')
            return redirect('services:my_applications')

        messages.success(self.request, 'Your freelance proposal has been submitted.')
        return redirect('services:my_applications')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        return context


class MyServiceApplicationsView(LoginRequiredMixin, generic.ListView):
    model = ServiceApplication
    template_name = 'services/my_applications.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return ServiceApplication.objects.filter(freelancer=self.request.user).select_related('listing').order_by('-created_at')
