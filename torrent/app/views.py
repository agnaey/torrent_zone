from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
import os
from django.core.mail import send_mail
from django.http import FileResponse, Http404,HttpResponseRedirect
from django.db.models import Avg
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.conf import settings
from django.urls import reverse
import razorpay
import json
import io
import zipfile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# Create your views here.


def login(req):
    if 'admin' in req.session:
        return redirect(admin_home)
    if 'username'in req.session:
        return redirect(index)
    else:
        if req.method=='POST':
            username = req.POST.get("username") 
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
    if req.method == 'POST':
        username = req.POST.get('username', '').strip()
        email = req.POST.get('Email', '').strip()
        password = req.POST.get('password', '').strip()

        # Validate input fields
        if not username or not email or not password:
            messages.error(req, "All fields are required!")
            return redirect(register)

        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(req, "Invalid email format!")
            return redirect(register)

        # Password length validation
        if len(password) < 6:
            messages.error(req, "Password must be at least 6 characters long!")
            return redirect(register)

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.warning(req, "Email is already registered!")
            return redirect(register)

        # Create user
        try:
            data = User.objects.create_user(
                first_name=username, username=email, email=email, password=password
            )
            data.save()

            # Send confirmation email
            send_mail(
                'GAME HAVEN',
                'GAME HAVEN Account Created Successfully',
                settings.EMAIL_HOST_USER,
                [email],
            )

            return redirect(login)

        except Exception as e:
            messages.error(req, f"Error: {str(e)}")
            return redirect(register)

    return render(req, 'register.html')
    
def fake_index(request):
    if 'username' in request.session :
        return redirect(index) 
    
    games=Game.objects.all().order_by("?")
    paid_games = Game.objects.filter(is_paid=True)
    free_games = Game.objects.filter(is_paid=False)

    return render(request, 'fake_index.html',{'games':games,'paid_games':paid_games,'free_games':free_games})

def fake_sec(req,id):
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
    
    return render(req,'fake_sec.html',context)

def fake_search(request):
    if request.method == 'POST':
        search = request.POST.get('search', '')  
        results = Game.objects.filter(title__icontains=search) if search else []
        return render(request, 'fake_search.html', {'search': search, 'results': results})
    else:
        return render(request, 'fake_search.html', {'search': '', 'results': []})


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

    return render(req, 'admin/game_details.html', context)    

def delete_review_admin(request,id):
    review = get_object_or_404(Review, id=id)
    review.delete()
    return redirect(game_details, id=review.game.id)

def admin_view_review(request, id):
    game = get_object_or_404(Game, id=id)
    reviews = Review.objects.filter(game=game)[::-1]
    return render(request, 'admin/admin_view_review.html', {'game': game, 'reviews': reviews})

def view_all_report(request):
    reports = Report.objects.select_related('game', 'user').order_by('-created_at')
    return render(request, 'admin/admin_report.html', {'reports': reports})

def delete_report(req,id):
    report=Report.objects.get(id=id)
    report.delete()
    return redirect('view_all_report')

def add_game(req):
        if req.method == 'POST':
            title = req.POST['title']
            des = req.POST.get('des', '')
            genre = req.POST['genre']
            developer = req.POST['developer']
            release_date = req.POST['release_date']

            image = req.FILES.get('image')
            torrent = req.FILES.get('torrent')

            is_paid = 'is_paid' in req.POST
            price = req.POST.get('price', None)

            if price in [None, '']:
                price = 0
            else:
                try:
                    price = int(price) 
                except ValueError:
                    price = 0
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

        game_requirement, created = GameRequirement.objects.get_or_create(
            game=game,  
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

def admin_add_review(request, id):
    if request.method == "POST":
        review_text = request.POST.get('comment')
        rating = request.POST.get('rating')

        if not review_text:
            return redirect('game_details', id=id)
        game = get_object_or_404(Game, id=id)
        Review.objects.create(user=request.user, game=game, comment=review_text, rating=rating or 0)
        return redirect(game_details, id=id)
    
    return redirect('game_details', id=id)

def admin_search(request):
    if request.method == 'POST':
        search = request.POST.get('search', '')  
        results = Game.objects.filter(title__icontains=search) if search else []
        return render(request, 'admin/admin_search.html', {'search': search, 'results': results})
    else:
        return render(request, 'admin/admin_search.html', {'search': '', 'results': []})
    
def user_downloads(request):
    orders = Order.objects.filter(game__is_paid=True).order_by('-id')
    total_profit = sum(order.game.price for order in orders)  # Sum up all game prices
    return render(request, 'admin/admin_downloads.html', {'orders': orders, 'total_profit': total_profit})


def delete_report(req,id):
    report = Report.objects.get(pk=id)
    report.delete()
    return redirect('view_all_report')

# def delete_download(req,id):
#     report = DownloadHistory.objects.get(pk=id)
#     report.delete()
#     return redirect('delete_download')

def resolve_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.resolved = True 
    report.save()

    send_mail(
        subject="Your Game Report Has Been Resolved",
        message=f"Hello {report.user.username},\n\nYour report regarding '{report.game.title}' has been resolved.\n\nThank you for your feedback!\n\n- GameHaven Team",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[report.user.email],
        fail_silently=False,
    )

    return redirect('view_all_report') 
# --------------user--------------------

def index(request):
    games=Game.objects.all().order_by("?")
    paid_games = Game.objects.filter(is_paid=True)
    free_games = Game.objects.filter(is_paid=False)

    return render(request, 'user/index.html',{'games':games,'paid_games':paid_games,'free_games':free_games})

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
    cart= Cart.objects.filter(user=request.user)[::-1]
    total_price = sum(item.total_price() for item in cart)
    return render(request, 'user/cart.html', {'cart': cart,'total_price':total_price})

def all_download(req):
    game = Cart.objects.all()
    cart_items = Cart.objects.filter(user=req.user)

    return render(req,'user/all_download.html',{'game':game,'cart_items':cart_items})

def order_payment2(req):
    if 'username' in req.session:
        user = User.objects.get(username=req.session['username'])
        cart_item = Cart.objects.filter(user=user)
        amount = sum(item.total_price() for item in cart_item)
        print(amount)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": int(amount) * 100, 
            "currency": "INR",
            "payment_capture": "1"
        })
        order_id=razorpay_order['id']
        price = 0
        for i in cart_item:
            price+=i.game.price
            order = Order.objects.create(
                user=user,
                game=i.game,
                price=i.game.price,
                provider_order_id=order_id
            )
            order.save()

        return render(req, "user/cart.html", {
            "callback_url": "http://127.0.0.1:8000/callback2/",
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "price": amount*100,
            "order_id": order_id
        })
    else:
        return redirect('login') 

@csrf_exempt
def callback2(request):

    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)
    print('user out')
    if "razorpay_signature" in request.POST:
        print('user in')
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")

        # Update Buy model with payment details
        order = Order.objects.filter(provider_order_id=provider_order_id)
        for i in order:

            i.payment_id = payment_id
            i.signature_id = signature_id
            # i.save()

            if not verify_signature(request.POST):
                i.status = PaymentStatus.SUCCESS
                # i.save()
                # return redirect('buy_all') 
            else:
                i.status = PaymentStatus.FAILURE
            i.save()
        return redirect("all_download")

    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id =json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        for i in order:
        # order.payment_id = payment_id
            i.status = PaymentStatus.FAILURE
            i.save()

        return render(request, "user/history.html")

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

def download(req,id):
    game = get_object_or_404(Game, pk=id)
    return render(req,'user/download.html',{'game':game})


def buy_all(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items.exists():
        return redirect('cart') 
    
    for item in cart_items:
        game = item.game
        if game.price == 0.00:
            DownloadHistory.objects.create(user=request.user, game=game)
        else:
            Purchase.objects.create(user=request.user, game=game)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for item in cart_items:
            game = item.game
            file_path = game.torrent.path
            if os.path.exists(file_path):
                zip_file.write(file_path, arcname=os.path.basename(file_path))
            else:
                raise Http404(f"File for {game} not found.")
    
    cart_items.delete()
    
    zip_buffer.seek(0)
    response = FileResponse(zip_buffer, as_attachment=True, filename="purchased_games.zip")
    return response


def order_payment(req,id):
    if 'username' in req.session:
        user = User.objects.get(username=req.session['username'])
        game = Game.objects.get(pk=id)
        amount = game.price

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": int(amount) * 100, 
            "currency": "INR",
            "payment_capture": "1"
        })
        order_id=razorpay_order['id']
        order = Order.objects.create(
            user=user,
            game=game,
            price=amount,
            provider_order_id=order_id
        )
        order.save()

        return render(req, "user/sec.html", {
            "callback_url": "http://127.0.0.1:8000/callback/",
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order": order,
        })
    else:
        return redirect('login') 

@csrf_exempt
def callback(request):

    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")

        # Update Buy model with payment details
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()

        if not verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            return redirect('download',id=order.game.id) 
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            return redirect("download",id=order.game.id)

    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id =json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        # order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()

        return render(request, "user/history.html")


    


def history(request):
    purchases = Purchase.objects.filter(user=request.user)[::-1]
    downloads = DownloadHistory.objects.filter(user=request.user)[::-1]
    context = {
        'purchases': purchases,
        'downloads': downloads,
    }
    return render(request, 'user/history.html', context)


def delete_purchase(request, id):
    purchase = get_object_or_404(Purchase, id=id, user=request.user)
    purchase.delete()
    return redirect('history')

def delete_download(request, id):
    download = get_object_or_404(DownloadHistory, id=id, user=request.user)
    download.delete()
    return redirect('history')

def search(request):
    if request.method == 'POST':
        search = request.POST.get('search', '')  
        results = Game.objects.filter(title__icontains=search) if search else []
        return render(request, 'user/search.html', {'search': search, 'results': results})
    else:
        return render(request, 'user/search.html', {'search': '', 'results': []})

