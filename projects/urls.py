from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('trainer-panel/', views.TraineeEvaluationListView.as_view(), name='trainer_panel'),
    path('add/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ProjectEditView.as_view(), name='edit'),
    path('<int:pk>/ai-assist/', views.AIProjectSummaryView.as_view(), name='ai_assist'),
    path('<int:pk>/evaluate/', views.TrainerEvaluationView.as_view(), name='evaluate'),
    path('portfolio/<int:pk>/', views.TraineePortfolioView.as_view(), name='portfolio'),
    path('award-badge/<int:trainee_pk>/', views.AwardBadgeView.as_view(), name='award_badge'),
]
