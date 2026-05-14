from django.urls import path
from . import views

app_name = 'opportunities'

urlpatterns = [
    path('', views.OpportunityListView.as_view(), name='list'),
    path('create/', views.OpportunityCreateView.as_view(), name='create'),
    path('<int:pk>/', views.OpportunityDetailView.as_view(), name='detail'),
    path('<int:pk>/apply/', views.ApplicationCreateView.as_view(), name='apply'),
    path('<int:pk>/ai-cover-letter/', views.ai_cover_letter, name='ai_cover_letter'),
    path('my-applications/', views.MyApplicationsView.as_view(), name='my_applications'),
    path('ai-match/', views.AIMatchView.as_view(), name='ai_match'),
]
