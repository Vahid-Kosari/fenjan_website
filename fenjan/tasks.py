from celery import shared_task
from django.utils import timezone
from fenjan.models import Customer, RegistrationState
from datetime import timedelta


@shared_task
def update_registration_states():
    now = timezone.now().date()
    customers = Customer.objects.all()

    for customer in customers:
        default_expiration_date = customer.registration_date + timedelta(days=3)

        if customer.expiration_date < now:
            customer.registration_state = RegistrationState.EXPIRED
        else:
            if customer.expiration_date > default_expiration_date:
                customer.registration_state = RegistrationState.REGISTERED
            else:
                customer.registration_state = RegistrationState.TRIAL
        customer.save()
