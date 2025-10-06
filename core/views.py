from django.shortcuts import render

def home(request):
    """Landing page view"""
    context = {"title": "Home"}
    return render(request, "home.html", context)


def about(request):
    """About page"""
    context = {"title": "About"}
    return render(request, "index.html", context)
