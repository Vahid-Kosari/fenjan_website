from django.shortcuts import render
from django.shortcuts import render, redirect


def index(request):
    # base.html is temporarily used to run the project but it will be replaced by standard index and layout ones
    return render(request, "fenjan/index.html")
