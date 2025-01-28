from django.urls import path
from . import views

urlpatterns = [
    path('login',views.login),
    path('register',views.register),

    # ----------user------------------------------
    path('', views.index, name='index'),
    path('sec/<id>',views.sec),

]