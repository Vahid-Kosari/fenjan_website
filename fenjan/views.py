from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse

from .models import Customer, RegistrationState
from django.utils import timezone
from django.contrib import messages

import os
from django.http import HttpResponse
import subprocess

# from .linkedin import

import json


def index(request, stored_messages="None"):

    # Optionally retrieve messages from Django messages
    # stored_messages = stored_messages or messages.get_messages(request)
    stored_messages = request.GET.get("stored_messages", "")

    print("stored_messages from index", stored_messages)

    return render(
        request,
        "fenjan/index.html",
        {
            "year": timezone.now().year,
            "stored_messages": stored_messages,  # Pass stored_messages to the template
        },
    )


def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        print("name:", name)
        email = request.POST["email"]
        # Collect keywords from input fields
        keywords = [request.POST.get(f"keyword{i}", "") for i in range(1, 6)]
        # Remove empty keywords
        keywords = [keyword for keyword in keywords if keyword]

        # Split the name into first and last name
        if name and email:
            name_parts = name.split()
            if len(name_parts) > 1:
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:])
            else:
                first_name = name_parts[0]
                last_name = ""
        else:
            return redirect("register")

        # Use the first name as the username if last name is not provided
        username = (
            first_name
            if last_name == ""
            else f"{first_name}.{last_name}".replace(" ", "")
        )

        try:
            # Check if a customer with the provided email already exists
            customer = Customer.objects.filter(email=email).first()

            if customer:
                # Update existing customer
                customer.first_name = first_name
                customer.last_name = last_name
                customer.username = username
                customer.keywords = keywords
                customer.save()
                messages.success(request, "Information updated successfully!")
            else:
                # Create the customer
                customer = Customer.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    keywords=keywords,
                    registration_state=RegistrationState.TRIAL,
                )
                messages.success(request, "Registration successful!")
        except Exception as e:
            messages.error(request, f"Registration failed: {e}")

        # Add some debug prints to confirm message setting
        for message in messages.get_messages(request):
            print(message)

        # Get the stored messages
        stored_messages = "&".join(f"{m}" for m in messages.get_messages(request))
        # stored_messages = messages.get_messages(request)
        print("stored_messages", stored_messages)
        print("Type of stored_messages:", type(stored_messages))

        # Redirect to index view with messages as query parameters
        # return HttpResponseRedirect(reverse("index") + "?" + stored_messages)
        return HttpResponseRedirect(
            reverse("index") + "?stored_messages=" + stored_messages
        )

    # Add some debug prints to confirm message setting
    for message in messages.get_messages(request):
        print(message)

    return render(request, "fenjan/register.html")


def linkedin_runner(request):
    try:
        # Define the path to the linkedin.py script
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "fenjan",
            "linkedin.py",
        )

        # Run the linkedin.py script
        subprocess.run(["python", script_path], check=True)

        return HttpResponse("LinkedIn script ran successfully.")
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

    # return render(request, "fenjan/index.html")


def linkedin_sgai_runner(request):
    try:
        # Define the path to the linkedin.py script
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "fenjan",
            "linkedin_sgai.py",
        )

        # Run the linkedin.py script
        subprocess.run(["python", script_path], check=True)

        return HttpResponse("LinkedIn script ran successfully.")
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
