from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect("/problems/")  # ✅ Redirect here
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, "accounts/login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST.get("email", "")
        password = request.POST["password"]
        confirm_password = request.POST.get("confirm_password", "")

        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif email and User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        else:
            user = User.objects.create_user(
                username=username, 
                email=email,
                password=password
            )
            user.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("/auth/login/")

    return render(request, "accounts/register.html")

def logout_view(request):
    logout(request)
    return redirect('/') 
from django.http import HttpResponse

def home_view(request):
    return render(request, "accounts/home.html")

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

@login_required
def profile_view(request):
    """User profile view"""
    try:
        from problems.models import Submission
        user_submissions = Submission.objects.filter(user=request.user).order_by('-submitted_at')[:10]
        
        # Calculate statistics
        total_submissions = Submission.objects.filter(user=request.user).count()
        accepted_submissions = Submission.objects.filter(user=request.user, verdict="Accepted").count()
        
        solved_problems = Submission.objects.filter(
            user=request.user, 
            verdict="Accepted"
        ).values('problem').distinct().count()
        
        success_rate = round((accepted_submissions / total_submissions * 100), 1) if total_submissions > 0 else 0
    except ImportError:
        # Fallback if problems app isn't available
        user_submissions = []
        total_submissions = 0
        accepted_submissions = 0
        solved_problems = 0
        success_rate = 0
    
    context = {
        'user_submissions': user_submissions,
        'total_submissions': total_submissions,
        'accepted_submissions': accepted_submissions,
        'solved_problems': solved_problems,
        'success_rate': success_rate
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def update_profile(request):
    """Update user profile"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', user.email)
        
        # Check if email is already taken by another user
        if User.objects.filter(email=user.email).exclude(id=user.id).exists():
            messages.error(request, "This email is already in use by another account.")
        else:
            user.save()
            messages.success(request, "Profile updated successfully!")
        
        return redirect('profile')
    
    return redirect('profile')