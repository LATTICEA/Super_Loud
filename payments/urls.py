from django.urls import path
from .views import *

urlpatterns = [
    path('config/',stripe_config),
    path('create-checkout-session', create_checkout_session),
    path('create-checkout-subscription-session/<int:num>/<str:per>', create_checkout_subscription_session), # new
    path('success', success , name = 'SuccessPayment') ,
    path('canceled/', canceled , name = 'CanceledPayment') ,
    path('error/', error , name = 'ErrorPayment') , # new
    path('transactions', transactions, name='transactions'),
    path('cancel-subscription', cancel_subscription),
    path('reinstate-subscription', reinstate_subscription),
    path('switch-billing-period', switch_billing_period),
]