"""URL configuration for users app."""

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('switch-account/', views.switch_account, name='switch_account'),
    path('switch-account/<int:user_id>/', views.switch_account_to, name='switch_account_to'),
]
