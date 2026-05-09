from django.db.models import Q
from django.views import generic
from .models import Scholarship


class ScholarshipListView(generic.ListView):
    model = Scholarship
    template_name = 'scholarships/list.html'
    context_object_name = 'scholarships'
    paginate_by = 12

    def get_queryset(self):
        queryset = Scholarship.objects.filter(is_active=True).order_by('deadline')
        level = self.request.GET.get('level', '')
        query = self.request.GET.get('q', '')
        if level:
            queryset = queryset.filter(level=level)
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(provider__icontains=query) | Q(description__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level_choices'] = Scholarship._meta.get_field('level').choices
        context['query'] = self.request.GET.get('q', '')
        context['level'] = self.request.GET.get('level', '')
        return context


class ScholarshipDetailView(generic.DetailView):
    model = Scholarship
    template_name = 'scholarships/detail.html'
    context_object_name = 'scholarship'
