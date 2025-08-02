from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from rest_framework.authtoken.models import Token
from utilities.options import ID_TYPES, VEHICLE_TYPES, VEHICLE_COLORS, DRIVER_STATUS_CHOICES


# Create your models here.

class UserManager(BaseUserManager):
    """Custom user model manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('User must have an email address.'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Ensure that the transaction is committed before creating the token
        if not transaction.get_autocommit():
            transaction.commit()  # Ensure SQLite's FK checks are passed

        # Create an authentication token for the user
        Token.objects.create(user=user)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractUser):
    """Custom user model that uses email as the username field."""
    is_driver = models.BooleanField(default=False, verbose_name=_('is driver'))
    username = None  # Remove the username field
    first_name = None
    last_name = None
    avatar = models.ImageField(upload_to='accounts/avatars/', blank=True, null=True, verbose_name=_('avatar'))
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('full name'))
    email = models.EmailField(unique=True, verbose_name=_('email address'))
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."),
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('phone number') ,validators=[phone_regex])
    country = CountryField(blank=True, null=True, verbose_name=_('country'), default='GH')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_('date joined'))
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    is_staff = models.BooleanField(default=False, verbose_name=_('is staff'))
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.full_name.split(' ')[0]} ({self.email})"


class Driver(models.Model):
    """Model representing a driver."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver', verbose_name=_('user'))
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_TYPES, verbose_name=_('vehicle type'), null=True)
    vehicle_color = models.CharField(max_length=50, choices=VEHICLE_COLORS, verbose_name=_('vehicle color'), null=True)
    vehicle_plate_number = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name=_('vehicle plate number'))
    id_type = models.CharField(max_length=50, choices=ID_TYPES, verbose_name=_('ID type'), null=True)
    id_number = models.CharField(max_length=50, unique=True, verbose_name=_('ID number'), null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('date created'))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_('date updated'))
    approved = models.BooleanField(default=False, verbose_name=_('approved'))
    status = models.CharField(max_length=200, blank=True, null=True, choices=DRIVER_STATUS_CHOICES)
    online = models.BooleanField(default=False, verbose_name=_('online'))

    class Meta:
        verbose_name = _('driver')
        verbose_name_plural = _('drivers')
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.user.full_name.split(' ')[0]} ({self.vehicle_plate_number})"


class Subscriber(models.Model):
    email = models.EmailField(unique=False, verbose_name='Email Address')
    name = models.CharField(max_length=100, blank=True, null=True)
    accepted_mailing = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'
        ordering = ['-create_date']

    def __str__(self):
        return self.email



