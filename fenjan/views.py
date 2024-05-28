from django.shortcuts import render, redirect

from .models import Customer, RegistrationState
from django.utils import timezone

import json


def index(request):
    return render(request, "fenjan/index.html")


def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        # Collect keywords from input fields
        keywords = [request.POST.get(f"keyword{i}", "") for i in range(1, 6)]
        print("keywords:", keywords)

        # Split the name into first and last name
        name_parts = name.split()
        if len(name_parts) > 1:
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
        else:
            first_name = name_parts[0]
            last_name = ""

        # Use the first name as the username if last name is not provided
        username = (
            first_name
            if last_name == ""
            else f"{first_name}.{last_name}".replace(" ", "")
        )

        # Create the customer
        customer = Customer.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            keywords=json.dumps(keywords),
            registration_state=RegistrationState.TRIAL,
        )

        return redirect("index")

    return render(request, "fenjan/register.html")
