from django.db import models
from django.contrib.auth.models import User
from django.views.generic.list import ListView
from .constants import PaymentStatus
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _




# Create your models here.


class Game(models.Model):
    title = models.CharField(max_length=255)
    des = models.TextField()
    genre = models.CharField(max_length=100)
    developer = models.CharField(max_length=255)
    release_date = models.DateField()
    image = models.ImageField()
    torrent = models.FileField()
    count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)

    is_paid = models.BooleanField(default=False) 
    price = models.IntegerField()

    def __str__(self):
        return self.title

class GameRequirement(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name="requirements")
    os = models.CharField(max_length=255)
    processor = models.CharField(max_length=255)
    memory = models.CharField(max_length=255)  
    graphics = models.CharField(max_length=255)  

    def __str__(self):
        return f"Requirements for {self.game.title}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True) 
    quantity = models.PositiveIntegerField(default=1)
    def total_price(self):
        return self.quantity * self.game.price 

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} purchased {self.game.title}"

    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.game.title}"

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    issue = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user.username} on {self.game.title}"
    
class DownloadHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} downloaded {self.game.title}"


class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    game=models.ForeignKey(Game,on_delete=models.CASCADE)
    price=models.IntegerField()
    status=CharField(
        _("Payment Status"),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False
    )
    provider_order_id = models.CharField(
        _("Order ID"), max_length=40, null=False,blank=False
    )
    payment_id = models.CharField(
        _("Payment ID"),max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        _("Signature ID"), max_length=128, null=False, blank=False
    )

    def __str__(self):
        return f"{self.id}-{self.name}-{self.status}"



