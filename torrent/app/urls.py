from django.urls import path
from . import views

urlpatterns = [
    path('',views.login, name='login'),
    path('register',views.register),
    path('logout',views.logout),

    # -------------admin------------------------------
    path('admin_home', views.admin_home, name='admin_home'),
    path('add_game', views.add_game, name='add_game'),
    path('add_game_req/<id>', views.add_game_req, name='add_game_req'),


    # ----------user------------------------------
    path('index', views.index, name='index'),
    path('sec/<id>',views.sec),
    path('add_to_cart/<id>',views.add_to_cart, name='add_to_cart'),
    path('cart',views.view_cart, name='cart'),
    path('remove_cart/<id>',views.remove_cart, name='remove_cart'),

]