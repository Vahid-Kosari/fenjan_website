from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse

from .models import Customer, RegistrationState, LinkedInSearchResult
from django.utils import timezone
from django.contrib import messages

import os
from django.http import HttpResponse
import subprocess

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


def search_results(request):

    search_result = LinkedInSearchResult.objects.filter(user='6th.User').first()

    if search_result:
    # Pass the list of HTML content to the template
        context = {'html_content': search_result.html_content}
    else:
        context = {'message': 'No results found'}

    return render(request, 'fenjan/search_results.html', context)

    # Retrieve 'html_content' passed from main function or other methods
    # html_content = request.session.get('html_content', None)
    # html_content = all_positions_html_block_for_keywords_html_block

    # if not html_content:
        # If not found in session, you can call find_positions again or handle the error
        # html_content = find_positions()  # or another fallback
        # request.session['html_content'] = html_content  # Store it in session

    # Return the template with the context
    # return render(request, 'fenjan/search_results.html', {'results': html_content})
    query = request.GET.get('q')  # Get the search query
    temp_folder = os.path.join(os.path.dirname(__file__), "temp")
    file_path = os.path.join(temp_folder, "all_positions_html_block_for_keywords_html_block.html")
    the_file_path = os.path.join(temp_folder, "the_html_content.html")
    
    # Read the file content
    if os.path.exists(the_file_path):
        with open(the_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    else:
        content = "No results found."

    context = {
        'query': query,
        'content': content,
    }
    return render(request, 'fenjan/search_results.html', context)


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
