# -*- encoding: utf-8 -*-

from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
    path('verify/account/<str:verkey>', verify_user, name="verify"),
    path('not-verified', not_verified, name="not-verified"),

    path('accounts/not-subscribed', not_subscribed, name="not-subscribed"),
    
    path('forgot-password', reset1, name='reset1'),
    path('reset/account-password/<str:resetkey>', reset2, name='reset2'),
    
    path('profile-page', profile_page, name='profile-page'),
    path('profile-pic-change', profile_pic_change, name='profile-pic-change'),
    path('cover-pic-change', cover_pic_change, name='cover-pic-change'),

    path('user-list', user_list, name='user-list'),
    path('delete-user/<int:id>', delete_user, name='delete-user'),
    path('suspend-user/<int:id>', suspend_user, name='suspend-user'),
    path('view-details/<int:id>', view_details, name='view-details'),
    path('make-admin/<int:id>', make_admin, name='make-admin'),

    path('account-suspended', account_suspended, name='account-suspended'),

    path('delete-account-completely/<int:id>', delete_account_completely),
    path('delete-account', delete_account, name='delete-account'),

]