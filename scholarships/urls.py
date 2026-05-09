from django.urls import path
from . import views

app_name = 'scholarships'

urlpatterns = [
    path('', views.ScholarshipListView.as_view(), name='list'),
    path('<int:pk>/', views.ScholarshipDetailView.as_view(), name='detail'),
]
