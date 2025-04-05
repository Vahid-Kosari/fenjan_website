from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse

from .models import Customer, RegistrationState, LinkedInSearchResult
from django.utils import timezone
from django.contrib import messages

import os, sys
from django.http import HttpResponse
import subprocess

import json

"""
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
            "month": timezone.now(),
            "stored_messages": stored_messages,  # Pass stored_messages to the template
        },
    )
"""

def index(request):
    # Retrieve stored messages from Django's messages framework
    stored_messages = list(messages.get_messages(request))

    # Debugging: Print messages to check the values
    print("Stored messages from index:", stored_messages)

    # Pass the messages and current date information to the template
    return render(
        request,
        "fenjan/index.html",
        {
            "year": timezone.now().year,
            "month": timezone.now().strftime("%B"),  # Format month as full name (e.g., "March")
            "stored_messages": stored_messages,  # Ensure messages are passed as a list
        },
    )


def search_results(request, customer_email):
# def search_results(request):

    # Registration process

    # customer_email = request.GET.get('customer_email')
    customer = Customer.objects.get(email=customer_email)

    # Searchinig process with linkedin_runner

    search_result = LinkedInSearchResult.objects.filter(user=customer).first()

    if search_result:
    # Pass the list of HTML content to the template
        context = {'html_content': search_result.html_content,
                   'customer': customer.username,
                   }
    else:
        context = {'message': 'No results found'}

    return render(request, 'fenjan/search_results.html', context)


"""
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

    return render(request, "fenjan/index.html")
"""

def register(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()

        # Collect and clean keywords
        keywords = [request.POST.get(f"keyword{i}", "").strip() for i in range(1, 6)]
        keywords = [keyword for keyword in keywords if keyword]  # Remove empty keywords

        if not name or not email:
            messages.error(request, "Both name and email are required.")
            return redirect("register")

        # Split name into first and last name
        name_parts = name.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Generate username
        username = first_name if not last_name else f"{first_name}.{last_name}".replace(" ", "")

        try:
            # Check if the customer already exists
            print("created = Customer")
            customer, created = Customer.objects.get_or_create(email=email, defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "keywords": keywords,
                "registration_state": RegistrationState.TRIAL,
            })

            print("not created = Customer")
            if not created:
                if customer.registration_state != "Expired":
                    # Update existing customer
                    customer.first_name = first_name
                    customer.last_name = last_name
                    customer.username = username
                    customer.keywords = keywords
                    customer.save()
                    messages.success(request, "Information updated successfully!")
                else:
                    print(f"{customer.username}'s registration expired!")
                    messages.error(request, "Your registration has expired. Please renew.")
                    return redirect("index")
                    # sys.exit()
            else:
                messages.success(request, "Registration successful!")

            # ✅ Run LinkedIn search after registration
            # request.POST = request.POST.copy()  # Make request mutable
            # request.POST["customer"] = customer.id  # Pass customer instance
            # linkedin_runner(request)  # Run the function
            try:
                # Define the path to the linkedin.py script
                print("try = linkedin.py")

                script_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "fenjan",
                    "linkedin.py",
                )

                # Run linkedin.py with customer details
                result = subprocess.run(
                    ["python", script_path, str(customer.id), customer.username],  # Ensure everything is passed as a string
                    check=False, # ✅ Allow handling non-zero exit codes manually
                    text=True,
                    stdout=sys.stdout,  # Redirect output to real-time stdout
                    stderr=sys.stderr  # Redirect errors to real-time stderr
                )
                
                # print(f"LinkedIn script output: {result.stdout.decode()}")
                print(f"LinkedIn script output: {result.stdout}")

                if result.returncode == 1359:  # Registration expired
                    messages.error(request, "Your registration has expired. Please renew.")
                    return redirect("index")
                
                    # Collect stored messages properly
                    # stored_messages = "&".join([str(m) for m in messages.get_messages(request)])
                    # return HttpResponseRedirect(reverse("index") + f"?stored_messages={stored_messages}")



            except subprocess.CalledProcessError as e:
                # messages.error(request, f"LinkedIn search failed: {e.stderr.decode()}")
                # return redirect("index")
                # error_message = getattr(e, "stderr", "").strip() or "Unknown error"
                error_message = e.stderr.strip() if e.stderr else "Unknown error"
                print(f"LinkedIn search failed: {error_message}")  # Debugging
                messages.error(request, f"LinkedIn search failed: {error_message}")
                return redirect("index")
                # return HttpResponse(f"An error occurred: {e}")

            # ✅ Fetch search results for this customer
            search_result = LinkedInSearchResult.objects.filter(user=customer).first()
            if search_result:
                context = {"html_content": search_result.html_content,
                           "customer": customer.username,
                          }
            else:
                context = {
                           "customer": customer.username,
                           }

            # ✅ Render search_results.html with the search results
            return render(request, "fenjan/search_results.html", context)

        except Exception as e:
            print(f"Registration failed: {e}")
            messages.error(request, f"Registration failed: {e}")
            return redirect("register")
        else:
            print(f"{customer.username}'s registration expired!")

    return render(
        request,
        "fenjan/index.html",
        {
            "year": timezone.now().year,
            "month": timezone.now().strftime("%B"),  # Format month as full name (e.g., "March")
            "stored_messages": ["Should reach out through POST!"],  # Ensure messages are passed as a list
        },
    )

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

        # return HttpResponse("LinkedIn script ran successfully.")
        # Redirect to search_results page after script execution
        return redirect('search_results') 
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