from django.shortcuts import render
from .models import *

# Create your views here.


def login(req):
    return render(req, 'login.html')

def register(req):
    return render(req, 'register.html')


# --------------user--------------------

def index(request):
    games=Game.objects.all()
    return render(request, 'index.html',{'games':games})

def sec(req,id):
    game=Game.objects.get(id=id)
    try:
        requ = GameRequirement.objects.get(game=game)
    except GameRequirement.DoesNotExist:
        requ = None 

    try:
        review = Review.objects.get(game=game)
    except Review.DoesNotExist:
        review = None
    
    return render(req,'sec.html',{'game':game,'requ':requ,'review':review})


