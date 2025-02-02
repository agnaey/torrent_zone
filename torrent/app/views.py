from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
import os
from django.http import FileResponse, Http404
from django.db.models import Avg
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.conf import settings
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
    try:
        requ=GameRequirement.objects.get(game=game)
    except GameRequirement.DoesNotExist:
        requ=None

    return render(req, 'admin/game_details.html', {'game': game,'requ':requ})    

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

def edit_game(req, id):
    game = Game.objects.get(pk=id)
    
    if req.method == 'POST':
        game.title = req.POST.get('title', game.title)
        game.des = req.POST.get('des', game.des)
        game.genre = req.POST.get('genre', game.genre)
        game.developer = req.POST.get('developer', game.developer)
        game.release_date = req.POST.get('release_date', game.release_date)
        
        if 'image' in req.FILES:
            game.image = req.FILES['image']
        if 'torrent' in req.FILES:
            game.torrent = req.FILES['torrent']
        
        game.is_paid = 'is_paid' in req.POST
        price = req.POST.get('price')
        try:
            game.price = int(price) if price else 0
        except ValueError:
            game.price = 0

        game.save()
        return redirect(f'../edit_req/{game.id}')
    return render(req, 'admin/edit_game.html', {'game': game})


def edit_req(req, id):
    game = Game.objects.get(pk=id)
    try:
        requirement = GameRequirement.objects.get(game=game)
    except GameRequirement.DoesNotExist:
        requirement = None

    if req.method == 'POST':
        os_value = req.POST.get('os')
        processor_value = req.POST.get('processor')
        memory_value = req.POST.get('memory')
        graphics_value = req.POST.get('graphics')

        if requirement:
            requirement.os = os_value
            requirement.processor = processor_value
            requirement.memory = memory_value
            requirement.graphics = graphics_value
            requirement.save()
        else:
            requirement = GameRequirement.objects.create(
                game=game,
                os=os_value,
                processor=processor_value,
                memory=memory_value,
                graphics=graphics_value
            )
        return redirect('admin_home')

    return render(req, 'admin/edit_req.html', {'game': game, 'requ': requirement})



def delete_game(req, id):
    game = get_object_or_404(Game, pk=id)

    torrent_path = os.path.join(settings.MEDIA_ROOT, str(game.torrent))
    image_path = os.path.join(settings.MEDIA_ROOT, str(game.image))

    # Delete files if they exist
    if os.path.exists(torrent_path):
        os.remove(torrent_path)

    if os.path.exists(image_path):
        os.remove(image_path)

    # Delete game from database
    game.delete()

    return redirect('admin_home')

def delete_req(req, id):
    game = Game.objects.get(pk=id)
    try:
        requirement = GameRequirement.objects.get(game=game)
        requirement.delete()
    except GameRequirement.DoesNotExist:
        pass
    return redirect('admin_home')


    

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
        review = Review.objects.filter(game=game)
    except Review.DoesNotExist:
        review = None
    reviews = Review.objects.filter(game=game)
    total_reviews = reviews.count()

    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0


    my_review = Review.objects.filter(game=game, user=req.user).first() if req.user.is_authenticated else None
    
    
    context = {
        'game': game,
        'requ': requ,
        'reviews': reviews,
        'my_review': my_review,
        'total_reviews': total_reviews,
        'average_rating': round(average_rating, 1),
    }
    
    return render(req,'user/sec.html',context)

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

def report_game(request, id):
    game = get_object_or_404(Game, id=id)

    if request.method == "POST":
        issue = request.POST.get("issue")
        if not issue:
            return redirect('sec', id=id)
        Report.objects.create(user=request.user, game=game, issue=issue)
        return redirect('sec', id=id)
    
    return redirect(sec, id=id)

def add_review(request, id):
    if request.method == "POST":
        review_text = request.POST.get('comment')
        rating = request.POST.get('rating')

        if not review_text:
            return redirect('sec', id=id)
        game = get_object_or_404(Game, id=id)
        Review.objects.create(user=request.user, game=game, comment=review_text, rating=rating or 0)
        return redirect('sec', id=id)
    
    return redirect('sec', id=id)

def delete_review(request,id):
    review = get_object_or_404(Review, id=id, user=request.user)
    review.delete()
    return redirect('sec', id=review.game.id)


def view_review(request, id):
    game = get_object_or_404(Game, id=id)
    reviews = Review.objects.filter(game=game)[::-1]
    return render(request, 'user/all_reviews.html', {'game': game, 'reviews': reviews})

def buy_game(request, id):
    game = get_object_or_404(Game, pk=id)
    if game.price == 0.00:
        DownloadHistory.objects.create(user=request.user, game=game)
    else:
        Purchase.objects.create(user=request.user, game=game)
    file_path = game.torrent.path 
    
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return response
    else:
        raise Http404("File not found.")
    
def history(request):
    purchases = Purchase.objects.filter(user=request.user)
    downloads = DownloadHistory.objects.filter(user=request.user)
    context = {
        'purchases': purchases,
        'downloads': downloads,
    }
    return render(request, 'user/history.html', context)