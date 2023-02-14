from re import sub
from django.conf import settings
from django.shortcuts import render,redirect,HttpResponse
import stripe
from .models import subscription_details
from authentication.models import profilemodel,userpool
from datetime import date,timedelta

from django.contrib.auth.decorators import login_required

@login_required(login_url="/login/")
def pricing_page(request):
    template = 'subs/page-pricing.html'
    context = {'segment':'payments'}
    obj = profilemodel.objects.get(user=request.user)
    environment = settings.ENVIRONMENT
    context['environment'] = environment
    context['obj'] = obj
    if obj.verified:
        pass
    else:
        return redirect('/not-verified')
    if obj.is_suspended:
        return redirect('/account-suspended')
    if obj.is_admin == False:
        return render(request,'accounts/access-denied.html')
    subobj = find_sub_obj(obj)
    context['subobj'] = subobj
    context['savings'] = subobj.userpoolobj.users.count() * 3000
    return render(request,template,context)

@login_required(login_url="/login/")
def start_free_trial(request):
    template = 'subs/trial-success.html'
    context = {}
    obj = profilemodel.objects.get(user=request.user)
    if obj.is_admin == False:
        return render(request,'accounts/access-denied.html')
    if obj.verified:
        pass
    else:
        return redirect('/not-verified')
    if obj.is_suspended:
        return redirect('/account-suspended')
    subobj = find_sub_obj(obj)
    if subobj.trial_availed:
        return render(request,'subs/already-availed.html')
    subobj.periodtype = 'Trial'
    subobj.start_date = date.today()
    subobj.next_date = date.today() + timedelta(days=7)
    subobj.trial_availed = True
    subobj.active = True
    subobj.save()
    context['ending'] = subobj.next_date
    return render(request,template,context)

def find_sub_obj(userprof):
    try:
        poolobj = userpool.objects.get(user=userprof)
    except:
        for i in userpool.objects.all().order_by("-id"):
            if userprof in i.users.all():
                poolobj = i
                break
    subobj = subscription_details.objects.get(userpoolobj=poolobj)
    try:
        if subobj.next_date <= date.today():
            subobj.active = False
            subobj.save()
            stripe.api_key = settings.STRIPE_SECRET_KEY
            temp = stripe.Subscription.retrieve(
                subobj.stripeSubscriptionId
            )
            if temp['status'] == 'active':
                subobj.active = True
                if subobj.periodtype == 'Monthly':
                    tempdate = subobj.next_date + timedelta(days=30)
                    subobj.start_date = date.today()
                    subobj.next_date = tempdate
                else:
                    subobj.start_date = date.today()
                    subobj.next_date = subobj.next_date + timedelta(days=365)
            subobj.save()
    except:
        pass
    return subobj

# def run_subscription_payment_routine(request):
#     print("All payments to be made here")
#     return HttpResponse('done')