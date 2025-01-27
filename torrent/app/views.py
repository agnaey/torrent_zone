from django.shortcuts import render

# Create your views here.


def login(req):
    return render(req, 'login.html')

def register(req):
    return render(req, 'register.html')


# --------------user--------------------

def index(request):
    return render(request, 'index.html')
