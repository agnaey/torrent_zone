from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout

# Create your views here.


def login(req):
    if 'admin' in req.session:
        return redirect(admin_home)
    if 'username'in req.session:
        return redirect(index)
    else:
        if req.method=='POST':
            username = req.POST.get("username")  # Use .get() to avoid KeyError
            password = req.POST.get("password")
            data=authenticate(username=username,password=password)
            if data:
                auth_login(req,data)
                if data.is_superuser:
                    req.session['admin']=username
                    return redirect(admin_home)
                else:
                    req.session['username']=username
                    return redirect(index)
            else:
                messages.warning(req, "username or password invalid.") 
            return redirect(login)
        else:
            return render(req,'login.html')

def logout(req):
    auth_logout(req)
    req.session.flush()
    return redirect(login)

def register(req):
    if req.method=='POST':
        username = req.POST['username']
        email = req.POST['Email']
        password = req.POST['password']
        # send_mail('Flipkart','Flipkart Account Created Successfully',settings.EMAIL_HOST_USER,[email])
        try:
            data=User.objects.create_user(first_name=username,username=email,email=email,password=password)
            data.save()
            # messages.success(req, "User Registered Successfully")
            return redirect(login)
        except:
            messages.warning(req,'user details already exits') 
            return redirect(register)   
    else:
        return render(req,'register.html')

# -----------admin---------------------

def admin_home(req):
    if 'admin' in req.session:
        games=Game.objects.all()
        return render(req,'admin/admin_home.html',{'games':games})
    else:
        return redirect(login)

def game_details(req,id):
    game = Game.objects.get(pk=id)
    return render(req, 'admin/game_details.html', {'game': game})    

def add_game(req):
        if req.method == 'POST':
            title = req.POST['title']
            des = req.POST.get('des', '')
            genre = req.POST['genre']
            developer = req.POST['developer']
            release_date = req.POST['release_date']

            image = req.FILES.get('image')  # Handle optional file upload
            torrent = req.FILES.get('torrent')

            is_paid = 'is_paid' in req.POST
            price = req.POST.get('price', None)

            if price in [None, '']:
                price = 0
            else:
                try:
                    price = int(price)  # Convert price to integer
                except ValueError:
                    price = 0
            # Create the game object
            game = Game.objects.create(
                title=title,
                des=des,
                genre=genre,
                developer=developer,
                release_date=release_date,
                image=image,
                torrent=torrent,
                is_paid=is_paid,
                price=price
            )

            return redirect('add_game_req', id=game.id)

        return render(req, 'admin/add.html')


def add_game_req(req, id):
    game = Game.objects.get(pk=id)

    if req.method == 'POST':
        os = req.POST['os']
        processor = req.POST['processor']
        memory = req.POST['memory']
        graphics = req.POST['graphics']

        # Create the GameRequirement entry
        game_requirement, created = GameRequirement.objects.get_or_create(
            game=game,  # Get the existing GameRequirement if it exists
            defaults={
                'os': os,
                'processor': processor,
                'memory': memory,
                'graphics': graphics
            }
        )

        if not created:
            game_requirement.os = os
            game_requirement.processor = processor
            game_requirement.memory = memory
            game_requirement.graphics = graphics
            game_requirement.save()

        return redirect('admin_home')  
    return render(req, 'admin/add_req.html', {'game': game})

def edit_game(req,id):
    game=Game.objects.get(pk=id)
    # return redirect('admin_home')
    return render(req, 'admin/edit_game.html', {'game': game})

def edit_req(req,id):
    game=Game.objects.get(pk=id)
    return render(req,'admin.edit_req.html',{'game':game})

    

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
    log_user=User.objects.get(username=request.session['username'])
    game = Game.objects.get(id=id)
    cart = Cart.objects.create(user=log_user,game=game)
    cart.save()
    
    return redirect(view_cart) 

@login_required(login_url='login') 
def view_cart(request):
    cart= Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart)
    return render(request, 'user/cart.html', {'cart': cart,'total_price':total_price})

def remove_cart(request, id):
    cart = Cart.objects.get(id=id)
    cart.delete()
    return redirect(view_cart)
