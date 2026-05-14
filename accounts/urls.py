from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/<str:username>/', views.public_profile_view, name='public_profile'),
    path('profile/<str:username>/qr/', views.profile_qr_view, name='profile_qr'),
    path('profile/<str:username>/qr/print/', views.qr_print_view, name='qr_print'),
    path('ai-assist/', views.profile_ai_assist, name='ai_assist'),
]
