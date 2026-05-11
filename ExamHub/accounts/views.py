from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import UpdateProfileForm, UpdatePictureForm, ChangePasswordForm
from .models import Profile
from exam.models import ExamAttempt, Exam, Question, StudentAnswer 


# Create your views here.
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "You're logged in!")
            return redirect('/')  # change to your home URL name
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/login.html')

@login_required
def profile(request):
    section = request.GET.get('section', 'profile')
    profile, created = Profile.objects.get_or_create(user=request.user)

    user_form = UpdateProfileForm(instance=request.user)
    picture_form = UpdatePictureForm(instance=profile)
    password_form = ChangePasswordForm(user=request.user)

    if request.method == 'POST':
        if section == 'update_profile':
            user_form = UpdateProfileForm(request.POST, instance=request.user)
            picture_form = UpdatePictureForm(request.POST, request.FILES, instance=profile)
            if user_form.is_valid() and picture_form.is_valid():
                user_form.save()
                picture_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('/profile/?section=profile')

        elif section == 'password':
            password_form = ChangePasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)  # keeps user logged in
                messages.success(request, 'Password changed successfully.')
                return redirect('/profile/?section=password')

    # Exam stats
    attempts = ExamAttempt.objects.filter(student=request.user).order_by('-submitted_at')
    created_exams = Exam.objects.filter(created_by=request.user)

    return render(request, 'accounts/profile.html', {
        'section': section,
        'profile': profile,
        'user_form': user_form,
        'picture_form': picture_form,
        'password_form': password_form,
        'attempts': attempts,
        'created_exams': created_exams,
    })
    

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You've been logged out.")
    return redirect('login')
    
def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created! Welcome.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/register.html', {'form': form})    