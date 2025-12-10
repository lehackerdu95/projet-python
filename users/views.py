"""
Views for the users application.
Handles user authentication and profile management.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm


class UserRegisterView(CreateView):
    """Register a new user."""
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')


def user_login(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            context = {'error': 'Invalid username or password'}
            return render(request, 'users/login.html', context)
    
    return render(request, 'users/login.html')


def user_logout(request):
    """Handle user logout."""
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    """Display user profile."""
    context = {'user': request.user}
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile information."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {'form': form, 'user': request.user}
    return render(request, 'users/profile_edit.html', context)


@login_required
def switch_account(request):
    """Display all accounts for switching."""
    all_users = User.objects.all().order_by('username')
    current_user = request.user
    
    context = {
        'all_users': all_users,
        'current_user': current_user
    }
    return render(request, 'users/switch_account.html', context)


@login_required
def switch_account_to(request, user_id):
    """Switch to another account (admin/staff only)."""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to switch accounts.')
        return redirect('home')
    
    try:
        target_user = User.objects.get(id=user_id)
        # Log out current user
        logout(request)
        # Log in as target user
        login(request, target_user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f'Switched to account: {target_user.username}')
        return redirect('home')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('switch_account')
