from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta


def default_expiration_date():
    return timezone.now().date() + timedelta(days=3)


# Constants for registration states
class RegistrationState(models.TextChoices):
    TRIAL = "Trial", "Trial"
    REGISTERED = "Registered", "Registered"
    EXPIRED = "Expired", "Expired"


class Customer(AbstractUser):
    registration_state = models.CharField(
        max_length=10,
        choices=RegistrationState.choices,
        default=RegistrationState.TRIAL,
    )
    keywords = models.JSONField(null=False)
    registration_date = models.DateField(default=timezone.now().date)
    expiration_date = models.DateField(default=default_expiration_date)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customer_set",  # Unique related_name for groups
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customer_permission_set",  # Unique related_name for user_permissions
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return self.username
