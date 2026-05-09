from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import MentorshipRequestForm
from .models import Mentor, MentorshipRequest


class MentorListView(generic.ListView):
    model = Mentor
    template_name = 'mentorship/list.html'
    context_object_name = 'mentors'
    paginate_by = 10

    def get_queryset(self):
        queryset = Mentor.objects.filter(is_active=True)
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(expertise__icontains=query) | Q(organisation__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class MentorDetailView(generic.DetailView):
    model = Mentor
    template_name = 'mentorship/detail.html'
    context_object_name = 'mentor'


class MentorshipRequestCreateView(LoginRequiredMixin, generic.CreateView):
    model = MentorshipRequest
    form_class = MentorshipRequestForm
    template_name = 'mentorship/request.html'

    def dispatch(self, request, *args, **kwargs):
        self.mentor = get_object_or_404(Mentor, pk=kwargs['pk'], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        mentorship_request = form.save(commit=False)
        mentorship_request.student = self.request.user
        mentorship_request.mentor = self.mentor
        mentorship_request.save()
        messages.success(self.request, 'Your mentorship request has been sent.')
        return redirect('mentorship:my_mentors')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mentor'] = self.mentor
        return context


class MyMentorsView(LoginRequiredMixin, generic.ListView):
    model = MentorshipRequest
    template_name = 'mentorship/my_mentors.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return MentorshipRequest.objects.filter(student=self.request.user).select_related('mentor').order_by('-created_at')
