from cffi.cffi_opcode import CLASS_NAME
from django.contrib.auth import views as auth_views
from django.views import View
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth import login, logout
from .forms import (
    CustomAuthForm,
    CustomUserCreationForm,
    CustomUserChangeForm,
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm
)
from .models import User

# Login view
class CustomLoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    authentication_form = CustomAuthForm

    def get_success_url(self):
        return reverse_lazy('home')


# Registration view
class UserRegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Save the avatar file, if present
        avatar = self.request.FILES.get('avatar')
        if avatar:
            self.object.avatar = avatar
            self.object.save()

        login(self.request, self.object)
        return response

# Profile update view
class UserProfileUpdateView(UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'registration/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

# Password change view
class CustomPasswordChangeView(auth_views.PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('password_change_done')

# Password reset views
class CustomPasswordResetView(auth_views.PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomLogoutView(View):
    @staticmethod
    def get(request):
        logout(request)
        return redirect('home')
