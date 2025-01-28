from django.db import models
from django.contrib.auth.models import User
from django.views.generic.list import ListView



# Create your models here.


class Game(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.CharField(max_length=100)
    developer = models.CharField(max_length=255)
    release_date = models.DateField()
    image = models.ImageField()
    torrent_file = models.FileField()
    download_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)

    is_paid = models.BooleanField(default=False) 
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

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


class DownloadHistoryView(ListView):
    model = DownloadHistory
    template_name = "user_downloads.html"

    def get_queryset(self):
        return DownloadHistory.objects.filter(user=self.request.user)




