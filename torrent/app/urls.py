from django.urls import path
from . import views

urlpatterns = [
    path('login',views.login, name='login'),
    path('register',views.register),

    # ----------user------------------------------
    path('', views.index, name='index'),
    path('sec/<id>',views.sec),
    path('add_to_cart/<id>',views.add_to_cart, name='add_to_cart'),
    path('cart',views.view_cart, name='cart'),

]