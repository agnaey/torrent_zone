from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('',views.fake_index, name='fake_index'),

    path('login',views.login, name='login'),
    path('register',views.register),
    path('logout',views.logout),
    path('fake_sec/<id>',views.fake_sec, name='fake_sec'),
    path('fake_search',views.fake_search, name='fake_search'),


    # -------------admin------------------------------
    path('admin_home', views.admin_home, name='admin_home'),
    path('game_detail/<id>',views.game_details,name="game_detail"),
    path('delete_review_admin/<id>',views.delete_review_admin, name='delete_review_admin'),
    path('admin_view_review/<id>',views.admin_view_review, name='admin_view_review'),
    path('view_all_report',views.view_all_report, name='view_all_report'),

    path('add_game', views.add_game, name='add_game'),
    path('add_game_req/<id>', views.add_game_req, name='add_game_req'),
    path('edit_game/<id>',views.edit_game),
    path('edit_req/<id>',views.edit_req),
    path('delete_game/<id>',views.delete_game),
    path('delete_req/<id>',views.delete_req, name='delete_req'),
    path('delete_report/<id>',views.delete_report,name='delete_report'),
    path('admin_add_review/<id>',views.admin_add_review, name='admin_add_review'),
    path('admin_search',views.admin_search, name='admin_search'),
    path('user_downloads', views.user_downloads, name='user_downloads'),
    path('delete_report/<id>',views.delete_report,name='delete_report'),
    path('resolve_report/<report_id>',views.resolve_report,name='resolve_report'),

    # ----------user------------------------------
    path('index', views.index, name='index'),
    path('sec/<id>',views.sec, name='sec'),
    path('add_to_cart/<id>',views.add_to_cart, name='add_to_cart'),
    path('cart',views.view_cart, name='cart'),
    path('remove_cart/<id>',views.remove_cart, name='remove_cart'),
    path('report_game/<id>',views.report_game, name='report_game'),
    path('add_review/<id>',views.add_review, name='add_review'),
    path('delete_review/<id>',views.delete_review, name='delete_review'),
    path('view_review/<id>',views.view_review, name='view_review'),
    path('buy/<id>/', views.buy_game, name='buy_game'),
    path('download/<id>',views.download,name='download'),
    path('all_download',views.all_download,name='all_download'),


    path('buy_all', views.buy_all, name='buy_all'),

    path('history', views.history, name='history'),
    path('delete_purchase/<id>', views.delete_purchase, name='delete_purchase'),
    path('delete_download/<id>',views.delete_download,name='delete_download'),
    path('search',views.search, name='search'),

    path('order_payment/<id>', views.order_payment, name='order_payment'),
    path('callback/', views.callback, name='callback'),

    path('order_payment2', views.order_payment2, name='order_payment2'),
    path('callback2/', views.callback2, name='callback2'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_form.html', extra_context={'reset_done': True}), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_form.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_form.html', extra_context={'reset_complete': True}), name='password_reset_complete'),
    
]