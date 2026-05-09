from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.ServiceListView.as_view(), name='list'),
    path('ai-support/', views.AISupportView.as_view(), name='ai_support'),
    path('<int:pk>/', views.ServiceDetailView.as_view(), name='detail'),
    path('<int:pk>/apply/', views.ServiceApplyView.as_view(), name='apply'),
    path('my-applications/', views.MyServiceApplicationsView.as_view(), name='my_applications'),
]
