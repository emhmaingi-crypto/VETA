import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import generic
from anthropic import Anthropic
from .forms import ApplicationForm, OpportunityForm
from .models import Application, Opportunity, PartnerOrganisation


class OpportunityListView(generic.ListView):
    model = Opportunity
    template_name = 'opportunities/list.html'
    context_object_name = 'opportunities'
    paginate_by = 12

    def get_queryset(self):
        queryset = Opportunity.objects.filter(is_active=True).order_by('-deadline')
        query = self.request.GET.get('q', '')
        opp_type = self.request.GET.get('type', '')
        level = self.request.GET.get('level', '')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query) | Q(skills_required__icontains=query)
            )
        if opp_type:
            queryset = queryset.filter(type=opp_type)
        if level:
            queryset = queryset.filter(level_required=level)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = Opportunity._meta.get_field('type').choices
        context['levels'] = Opportunity._meta.get_field('level_required').choices
        context['query'] = self.request.GET.get('q', '')
        return context


class OpportunityDetailView(generic.DetailView):
    model = Opportunity
    template_name = 'opportunities/detail.html'
    context_object_name = 'opportunity'


class ApplicationCreateView(LoginRequiredMixin, generic.CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'opportunities/apply.html'

    def dispatch(self, request, *args, **kwargs):
        self.opportunity = get_object_or_404(Opportunity, pk=kwargs['pk'], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        application = form.save(commit=False)
        application.student = self.request.user
        application.opportunity = self.opportunity
        application.ai_match_score = None
        application.save()
        messages.success(self.request, 'Your application has been submitted.')
        return redirect('opportunities:my_applications')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opportunity'] = self.opportunity
        return context


class MyApplicationsView(LoginRequiredMixin, generic.ListView):
    model = Application
    template_name = 'opportunities/applications.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user).select_related('opportunity').order_by('-created_at')


class AIMatchView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'opportunities/ai_match.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        opportunities = list(Opportunity.objects.filter(is_active=True).order_by('-deadline')[:20])
        context['matches'] = []
        prompt = self.build_prompt(user, opportunities)
        ai_key = settings.ANTHROPIC_API_KEY

        if not ai_key:
            context['error'] = 'AI matching is not configured. Add ANTHROPIC_API_KEY to your environment.'
            return context

        if not opportunities:
            context['error'] = 'No active opportunities are available for matching right now.'
            return context

        try:
            client = Anthropic(api_key=ai_key)
            response = client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=800,
                temperature=0.0,
                messages=[{'role': 'user', 'content': prompt}],
            )
            context['matches'] = self.parse_matches(response, opportunities)
            if not context['matches']:
                context['error'] = 'AI matching returned no valid results. Please try again later.'
        except json.JSONDecodeError:
            context['error'] = 'AI matching returned an unexpected format. Please try again later.'
        except Exception:
            context['error'] = 'AI matching is unavailable right now. Please try later.'

        return context

    def parse_matches(self, response, opportunities):
        if not getattr(response, 'content', None):
            return []

        raw_text = ''
        try:
            raw_text = response.content[0].text
        except (IndexError, AttributeError):
            return []

        payload = json.loads(raw_text)
        raw_matches = payload.get('matches', []) if isinstance(payload, dict) else []
        if not isinstance(raw_matches, list):
            return []

        opportunity_map = {opp.id: opp for opp in opportunities}
        parsed_matches = []

        for item in raw_matches:
            if not isinstance(item, dict):
                continue
            try:
                opp_id = int(item.get('id'))
                score = int(item.get('score'))
            except (TypeError, ValueError):
                continue

            opportunity = opportunity_map.get(opp_id)
            if not opportunity:
                continue

            parsed_matches.append({
                'id': opp_id,
                'score': max(0, min(score, 100)),
                'reason': str(item.get('reason', '')).strip(),
                'title': opportunity.title,
                'url': opportunity.get_absolute_url(),
            })

        return parsed_matches

    def build_prompt(self, user, opportunities):
        skills = user.skills or ''
        profile = (
            f"Name: {user.get_full_name()}\n"
            f"Course: {user.course}\n"
            f"Level: {user.level}\n"
            f"Skills: {skills}\n"
            f"Bio: {user.bio}"
        )
        blocks = [
            'You are an expert career advisor. Evaluate these opportunities for the student below.',
            'Return exactly valid JSON with a top 5 list of opportunity IDs, score 0-100, and a short reason for each match.',
            'Student profile:',
            profile,
            'Opportunities:',
        ]

        for opp in opportunities:
            requirements = opp.requirements or opp.description or 'No requirements provided.'
            blocks.append(
                f"{opp.id}. {opp.title} | Type: {opp.type} | Level: {opp.level_required or 'Any'} | Requirements: {requirements} | Skills: {opp.skills_required or 'None'}"
            )

        blocks.append('Output exactly: {"matches": [{"id": <id>, "score": <score>, "reason": "..."}]}')
        return '\n\n'.join(blocks)


class OpportunityCreateView(LoginRequiredMixin, generic.CreateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = 'opportunities/create.html'
    success_url = '/opportunities/'

    def form_valid(self, form):
        opportunity = form.save(commit=False)
        # Create or get partner organisation based on user
        if self.request.user.user_type in ['company', 'individual']:
            partner, created = PartnerOrganisation.objects.get_or_create(
                name=self.request.user.company_name or self.request.user.get_full_name(),
                defaults={
                    'type': 'Company' if self.request.user.user_type == 'company' else 'Individual',
                    'contact_email': self.request.user.email,
                }
            )
            opportunity.partner = partner
        else:
            # For students, maybe don't allow, or handle differently
            messages.error(self.request, 'Only companies and individuals can post opportunities.')
            return redirect('opportunities:create')

        opportunity.save()
        messages.success(self.request, 'Opportunity posted successfully.')
        return super().form_valid(form)
