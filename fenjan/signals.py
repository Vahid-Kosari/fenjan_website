from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Customer, RegistrationState


@receiver(pre_save, sender=Customer)
def update_registration_state(sender, instance, **kwargs):
    current_date = timezone.now().date()

    if current_date >= instance.expiration_date:
        instance.registration_state = RegistrationState.EXPIRED
    elif current_date <= instance.registration_date + timedelta(days=3):
        instance.registration_state = RegistrationState.TRIAL
    else:
        instance.registration_state = RegistrationState.REGISTERED
