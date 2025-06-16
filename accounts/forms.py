from django import forms
from django.db import transaction
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm
)
from django.utils.translation import gettext_lazy as _
from .models import User, Driver


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users with custom user model."""
    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone_number', 'country', 'avatar', 'is_driver')


class CustomUserChangeForm(UserChangeForm):
    """Form for updating existing users with custom user model."""
    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone_number', 'country', 'avatar', 'is_driver')


class CustomAuthForm(AuthenticationForm):
    """Custom authentication form using email as the username field."""
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with improved styling."""
    old_password = forms.CharField(
        label=_("Old password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter old password'})
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form using email."""
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Form to set a new password without the old password (e.g., via reset)."""
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )


class DriverRegistrationForm(UserCreationForm):
    """Form for driver registration, combining user and driver model fields."""

    vehicle_plate_number = forms.CharField(max_length=20)
    vehicle_type = forms.CharField(max_length=50)
    vehicle_color = forms.CharField(max_length=30)
    id_type = forms.CharField(max_length=30)
    id_number = forms.CharField(max_length=50)
    approved = forms.BooleanField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'full_name', 'phone_number', 'country', 'avatar', 'is_driver')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None

    field_order = ['email', 'full_name', 'phone_number', 'country', 'avatar', 'is_driver',
                   'vehicle_plate_number', 'vehicle_type', 'vehicle_color', 'id_type', 'id_number', 'approved']

    @transaction.atomic
    def save(self, commit=True):
        """Save the user and associated driver."""
        user = super().save(commit=False)
        user.is_driver = True
        if commit:
            user.save()
            Driver.objects.create(
                user=user,
                vehicle_plate_number=self.cleaned_data['vehicle_plate_number'],
                vehicle_type=self.cleaned_data['vehicle_type'],
                vehicle_color=self.cleaned_data['vehicle_color'],
                id_type=self.cleaned_data['id_type'],
                id_number=self.cleaned_data['id_number'],
                approved=self.cleaned_data.get('approved', False)
            )
        return user