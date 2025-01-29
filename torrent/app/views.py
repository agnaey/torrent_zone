from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *

# Create your views here.


def login(req):
    return render(req, 'login.html')

def register(req):
    return render(req, 'register.html')


# --------------user--------------------

def index(request):
    games=Game.objects.all()
    
    return render(request, 'user/index.html',{'games':games})

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
    
    return render(req,'user/sec.html',{'game':game,'requ':requ,'review':review})

@login_required
def add_to_cart(request, id):
    game = Game.objects.get(id=id)
    if not Cart.objects.filter(user=request.user, game=game).exists():
        Cart.objects.create(user=request.user, game=game, price=game.price)
    return redirect('add_to_cart') 

@login_required(login_url='login') 
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    return render(request, 'user/cart.html', {'cart_items': cart_items})
