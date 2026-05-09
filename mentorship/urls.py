from django.urls import path
from . import views

app_name = 'mentorship'

urlpatterns = [
    path('', views.MentorListView.as_view(), name='list'),
    path('<int:pk>/', views.MentorDetailView.as_view(), name='detail'),
    path('<int:pk>/request/', views.MentorshipRequestCreateView.as_view(), name='request'),
    path('my-mentors/', views.MyMentorsView.as_view(), name='my_mentors'),
]
