from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', User.ROLE_USER)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ROLE_SUPERADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as the unique identifier."""
    
    ROLE_SUPERADMIN = 'superadmin'
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'
    
    ROLE_CHOICES = (
        (ROLE_SUPERADMIN, _('Super Admin')),
        (ROLE_ADMIN, _('Admin')),
        (ROLE_USER, _('User')),
    )
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(_('biography'), blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def is_superadmin(self):
        return self.role == self.ROLE_SUPERADMIN
    
    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.role == self.ROLE_SUPERADMIN
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class UserProfile(models.Model):
    """Extended profile information for users."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    address = models.CharField(_('address'), max_length=255, blank=True)
    birth_date = models.DateField(_('birth date'), null=True, blank=True)
    preferred_language = models.CharField(
        _('preferred language'),
        max_length=2,
        choices=[('en', _('English')), ('ky', _('Kyrgyz')), ('ru', _('Russian'))],
        default='en'
    )
    
    def __str__(self):
        return f"Profile for {self.user.email}"
