import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic

from anthropic import Anthropic

from accounts.models import StudentUser
from .forms import AwardBadgeForm, ProjectForm, ProjectImageFormSet, TrainerEvaluationForm
from .models import Project, ProjectImage, RecognitionBadge, TrainerEvaluation


# ── helpers ──────────────────────────────────────────────────────────────────

def _ai_client():
    key = settings.ANTHROPIC_API_KEY
    if not key:
        return None
    return Anthropic(api_key=key)


# ── Project list / portfolio ──────────────────────────────────────────────────

class ProjectListView(generic.ListView):
    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        qs = Project.objects.filter(is_public=True).select_related('trainee').prefetch_related('images')
        q = self.request.GET.get('q', '')
        course = self.request.GET.get('course', '')
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(technologies__icontains=q)
                | Q(trainee__first_name__icontains=q)
                | Q(trainee__last_name__icontains=q)
            )
        if course:
            qs = qs.filter(course_area=course)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['course_choices'] = Project._meta.get_field('course_area').choices
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_course'] = self.request.GET.get('course', '')
        return ctx


class TraineePortfolioView(generic.ListView):
    """Public portfolio page for a single trainee."""
    template_name = 'projects/portfolio.html'
    context_object_name = 'projects'

    def get_queryset(self):
        self.trainee = get_object_or_404(StudentUser, pk=self.kwargs['pk'], user_type='student')
        return Project.objects.filter(trainee=self.trainee, is_public=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['trainee'] = self.trainee
        ctx['badges'] = RecognitionBadge.objects.filter(trainee=self.trainee)
        ctx['evaluations'] = TrainerEvaluation.objects.filter(
            trainee=self.trainee
        ).select_related('trainer').order_by('-created_at')[:5]
        ctx['avg_rating'] = self.trainee.average_rating
        return ctx


class ProjectDetailView(generic.DetailView):
    model = Project
    template_name = 'projects/detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        qs = Project.objects.select_related('trainee').prefetch_related('images', 'evaluations__trainer')
        if self.request.user.is_authenticated and self.request.user == self.get_object_candidate():
            return qs
        return qs.filter(is_public=True)

    def get_object_candidate(self):
        return Project.objects.filter(pk=self.kwargs['pk']).first()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['evaluations'] = self.object.evaluations.select_related('trainer').all()
        ctx['can_evaluate'] = (
            self.request.user.is_authenticated
            and self.request.user.is_trainer
            and not self.object.evaluations.filter(trainer=self.request.user).exists()
        )
        ctx['user_is_owner'] = (
            self.request.user.is_authenticated
            and self.request.user == self.object.trainee
        )
        return ctx


# ── Create / Edit project ─────────────────────────────────────────────────────

class ProjectCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/form.html'

    def test_func(self):
        return self.request.user.user_type == 'student'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['image_formset'] = ProjectImageFormSet(self.request.POST, self.request.FILES)
        else:
            ctx['image_formset'] = ProjectImageFormSet()
        ctx['action'] = 'Add'
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        image_formset = ctx['image_formset']
        form.instance.trainee = self.request.user
        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            messages.success(self.request, 'Project added to your showcase!')
            return redirect(self.object.get_absolute_url())
        return self.render_to_response(self.get_context_data(form=form))


class ProjectEditView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/form.html'

    def test_func(self):
        return self.get_object().trainee == self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['image_formset'] = ProjectImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            ctx['image_formset'] = ProjectImageFormSet(instance=self.object)
        ctx['action'] = 'Edit'
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        image_formset = ctx['image_formset']
        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            messages.success(self.request, 'Project updated.')
            return redirect(self.object.get_absolute_url())
        return self.render_to_response(self.get_context_data(form=form))


# ── AI summarize / expand ─────────────────────────────────────────────────────

class AIProjectSummaryView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    """AJAX-friendly view: AI summarizes or expands a project description."""

    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return project.trainee == self.request.user

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, trainee=request.user)
        action = request.POST.get('action', 'summarize')  # 'summarize' or 'expand'
        client = _ai_client()
        if not client:
            messages.error(request, 'AI is not configured. Add ANTHROPIC_API_KEY to your environment.')
            return redirect(project.get_absolute_url())

        if action == 'summarize':
            prompt = (
                f"You are an expert TVET career advisor. Summarize this student project description "
                f"into 2-3 concise, professional sentences suitable for a portfolio showcase:\n\n"
                f"Project title: {project.title}\n"
                f"Course area: {project.get_course_area_display()}\n"
                f"Technologies/tools: {project.technologies}\n\n"
                f"Description:\n{project.description}"
            )
        else:
            prompt = (
                f"You are an expert TVET career advisor. Expand this student project description "
                f"into a detailed, professional portfolio write-up that highlights technical skills, "
                f"problem-solving, outcomes, and industry relevance. Use clear paragraphs:\n\n"
                f"Project title: {project.title}\n"
                f"Course area: {project.get_course_area_display()}\n"
                f"Technologies/tools: {project.technologies}\n"
                f"Status: {project.get_status_display()}\n\n"
                f"Original description:\n{project.description}"
            )

        try:
            response = client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=800,
                temperature=0.3,
                messages=[{'role': 'user', 'content': prompt}],
            )
            result = response.content[0].text.strip()
            if action == 'summarize':
                project.ai_summary = result
            else:
                project.ai_expanded = result
            project.save(update_fields=['ai_summary'] if action == 'summarize' else ['ai_expanded'])
            messages.success(request, f'AI {"summary" if action == "summarize" else "expanded description"} generated successfully.')
        except Exception as exc:
            messages.error(request, f'AI error: {exc}')

        return redirect(project.get_absolute_url())


# ── Trainer evaluation ────────────────────────────────────────────────────────

class TrainerEvaluationView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = TrainerEvaluation
    form_class = TrainerEvaluationForm
    template_name = 'projects/evaluate.html'

    def test_func(self):
        return self.request.user.is_trainer

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['project'] = self.project
        return ctx

    def form_valid(self, form):
        form.instance.trainer = self.request.user
        form.instance.trainee = self.project.trainee
        form.instance.project = self.project
        evaluation = form.save()
        # Auto-award badge if rating is 5
        if evaluation.rating == 5:
            RecognitionBadge.objects.get_or_create(
                trainee=self.project.trainee,
                badge_type='top_rated',
                defaults={
                    'title': 'Top Rated Trainee',
                    'description': f'Outstanding rating awarded by {self.request.user.get_full_name()}',
                    'awarded_by': self.request.user,
                },
            )
        if evaluation.recommended_for_freelance:
            RecognitionBadge.objects.get_or_create(
                trainee=self.project.trainee,
                badge_type='trainer_pick',
                defaults={
                    'title': "Trainer's Pick for Freelance",
                    'description': f'Recommended for freelance work by {self.request.user.get_full_name()}',
                    'awarded_by': self.request.user,
                },
            )
        messages.success(self.request, f'Evaluation submitted for {self.project.trainee.get_full_name()}.')
        return redirect(self.project.get_absolute_url())


class TraineeEvaluationListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    """Trainer sees all trainees they can evaluate."""
    template_name = 'projects/trainer_panel.html'
    context_object_name = 'trainees'

    def test_func(self):
        return self.request.user.is_trainer

    def get_queryset(self):
        return StudentUser.objects.filter(user_type='student').annotate(
            project_count=Count('showcase_projects'),
            eval_count=Count('evaluations_received'),
        ).order_by('-project_count')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['recent_evaluations'] = TrainerEvaluation.objects.filter(
            trainer=self.request.user
        ).select_related('trainee', 'project').order_by('-created_at')[:10]
        return ctx


# ── Award badge ───────────────────────────────────────────────────────────────

class AwardBadgeView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = RecognitionBadge
    form_class = AwardBadgeForm
    template_name = 'projects/award_badge.html'

    def test_func(self):
        return self.request.user.is_trainer

    def dispatch(self, request, *args, **kwargs):
        self.trainee = get_object_or_404(StudentUser, pk=kwargs['trainee_pk'], user_type='student')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['trainee'] = self.trainee
        return ctx

    def form_valid(self, form):
        form.instance.trainee = self.trainee
        form.instance.awarded_by = self.request.user
        form.save()
        messages.success(self.request, f'Badge awarded to {self.trainee.get_full_name()}.')
        return redirect(reverse('projects:portfolio', args=[self.trainee.pk]))


# ── Leaderboard ───────────────────────────────────────────────────────────────

class LeaderboardView(generic.TemplateView):
    template_name = 'projects/leaderboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Top trainees by average trainer evaluation rating
        top_trainees_qs = (
            StudentUser.objects
            .filter(user_type='student', evaluations_received__isnull=False)
            .annotate(
                avg_eval=Avg('evaluations_received__rating'),
                eval_count=Count('evaluations_received'),
                project_count=Count('showcase_projects'),
            )
            .filter(eval_count__gte=1)
            .order_by('-avg_eval', '-project_count')[:20]
        )
        ctx['top_trainees'] = top_trainees_qs
        ctx['badge_holders'] = (
            StudentUser.objects
            .filter(user_type='student', badges__isnull=False)
            .annotate(badge_count=Count('badges'))
            .order_by('-badge_count')[:10]
        )
        ctx['recent_badges'] = RecognitionBadge.objects.select_related('trainee', 'awarded_by').order_by('-awarded_at')[:12]
        return ctx
