from django.urls import path
from .views import pricing_page, start_free_trial#, run_subscription_payment_routine

urlpatterns = [
    path('pricing-page',pricing_page,name='pricing-page'),
    path('start-free-trial',start_free_trial,name='start-free-trial'),
    # path('run-subscription-payment-routine',run_subscription_payment_routine),
]