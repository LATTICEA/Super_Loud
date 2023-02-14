from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http.response import JsonResponse
from django.contrib.auth import user_logged_in
from django.dispatch import receiver
import stripe
import json
from stripe.api_resources import customer
from authentication.models import profilemodel, userpool, User
from subscription.models import subscription_details
from subscription.views import find_sub_obj
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth.decorators import login_required



if settings.ENVIRONMENT != 'dev':
    single_user_pricing_model = {
        'Monthly':{
            'Data': 1
            , 'Data+Predictions': 1
        },
        'Annually':{
            'Data': 2
            , 'Data+Predictions': 2
        }
    }
else:
    single_user_pricing_model = {
        'Monthly':{
            'Data': 1500
            , 'Data+Predictions': 1500
        },
        'Annually':{
            'Data': 15000
            , 'Data+Predictions': 15000
        }
    }

# multi_user_pricing_model = {
#     'Monthly':{
#         'Data': 40
#         , 'Data+Predictions': 52
#     },
#     'Annually':{
#         'Data': 400
#         , 'Data+Predictions': 520
#     }
# }

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey' : settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe = False)

def find_charge_amount(profileobj, period):
    subobj = find_sub_obj(profileobj)

    try:
        if period == "m":
            period = "Monthly"
    except:
        pass

    try:
        if subobj.periodtype == "Monthly":
            period = "Monthly"
    except:
        pass


    # if subobj.userpoolobj.users.count() > 19:
    #     total_charge = multi_user_pricing_model[subobj.periodtype][subobj.subtype]
    # else:

    # print("period_type", period)
    # print("subscription type", subobj.subtype)
    # print(single_user_pricing_model[period][subobj.subtype])

    total_charge = single_user_pricing_model[period][subobj.subtype]
    
    try:
        number_of_days = datetime(subobj.next_date.year,subobj.next_date.month,subobj.next_date.day) - datetime.utcnow() 
    except Exception as e:
        print(e)

    if subobj.active == True:
        if settings.ENVIRONMENT == 'dev':
            if period == 'Monthly':
                amount = 100 * (total_charge * (number_of_days.days / 30))
                if amount > 100:
                    amount = 100
                else:
                    amount = amount
            else:
                amount = 100 * (total_charge * (number_of_days.days / 365))
                if amount > 200:
                    amount = 200
                else:
                    amount = amount
            return int(amount)
        else:
            if period == 'Monthly':
                amount = 100 * (total_charge * (number_of_days.days / 30))
                if amount > 150000: #1500 * 100 = 150,000
                    amount = 150000
                else:
                    amount = amount
            else:
                amount = 100 * (total_charge * (number_of_days.days / 365))
                if amount > 1500000: #15000 * 100 = 1,500,000
                    amount = 1500000
                else:
                    amount = amount
            return int(amount)
    else:
        if settings.ENVIRONMENT == 'dev':
            if period == 'Monthly':
                amount = 100 * total_charge
                if amount > 100:
                    amount = 100
                else:
                    amount = amount
            else:
                amount = 100 * total_charge
                if amount > 200:
                    amount = 200
                else:
                    amount = amount
            return int(amount)
        else:
            if period == 'Monthly':
                amount = 100 * total_charge
                if amount > 150000: #1500 * 100 = 150,000
                    amount = 150000
                else:
                    amount = amount
            else:
                amount = 100 * total_charge
                if amount > 1500000: #15000 * 100 = 1,500,000
                    amount = 1500000
                else:
                    amount = amount
            return int(amount)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        try:
            profile_id = request.GET['profile-id']
        except:
            return redirect('/error')

        if settings.DEBUG == True:
            domain_url = 'http://{}/'.format(request.get_host())
        else:
            domain_url = 'https://{}/'.format(request.get_host())
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            profileobj = profilemodel.objects.get(pk = profile_id)
            print('profileobj', profileobj)

            subobj = find_sub_obj(profileobj)
            print('subobj', subobj)

            subobj_period_type = subobj.periodtype
            print('subobj_period_type', subobj_period_type)

            subobj_sub_type = subobj.subtype
            print('subobj_sub_type', subobj_sub_type)

            checkout_session = stripe.checkout.Session.create(
                customer=subobj.stripeCustomerId
                , success_url=domain_url + 'success?session_id={}'.format(profile_id)
                , cancel_url=domain_url + 'canceled/'
                , payment_method_types=['card']
                , mode='payment'
                , line_items=[
                    {
                        'name': request.user.username,
                        'quantity': 1,
                        'currency': 'usd',
                        'amount': find_charge_amount(profileobj, subobj_period_type),
                        'description':'Adding user "{}" to your pool'.format(profileobj.user.username)
                    }
                ]
            )

            stripe.PaymentIntent.modify(
                checkout_session.payment_intent
                , metadata={
                    'invoice_description':'Added user "{}" to plan'.format(profileobj.user.username)
                }
            )

            template = 'payments/create-checkout-session.html'
            context = {'sessionId' : checkout_session['id']}
            return render(request,template,context)
           
        except Exception as e:
            return JsonResponse({'error': str(e)})

@csrf_exempt
def create_checkout_subscription_session(request,num,per):
    print("per date?", per)
    if request.method == 'GET':
        try:
            profile_id = request.GET['profile-id']
        except:
            return redirect('/error')

        if settings.DEBUG == True:
            domain_url = 'http://{}/'.format(request.get_host())
        else:
            domain_url = 'https://{}/'.format(request.get_host())
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            if per == "m":
                period = "Monthly"
        except:
            try:
                if subobj.periodtype == "Monthly":
                    period = "Monthly"
            except:
                pass

        # IS `per` A DATE OR PERIOD LIKE MONTHLY? 

        try:
            profileobj = profilemodel.objects.get(pk = profile_id)
            if profileobj.is_admin == False:
                return render(request,'accounts/access-denied.html')
            subobj = find_sub_obj(profileobj)
            if period == 'Monthly':
                pertype = 'm'
                if subobj.subtype == 'Data':
                    subtype = '1'
                elif subobj.subtype == 'Data+Predictions':
                    subtype = '3'
                else:
                    pertype,subtype = '1234','dsadas'
            elif period == 'Annually':
                pertype = 'y'
                if subobj.subtype == 'Data':
                    subtype = '1'
                elif subobj.subtype == 'Data+Predictions':
                    subtype = '3'
                else:
                    pertype,subtype = '1234','dsadas'
            else:
                pertype,subtype = '1234','dsadas'
            if per == pertype and str(num) == subtype:
                return redirect('/cancel-subscription/{}'.format(subobj.id))
            if subobj.stripeCustomerId:
                temp = {'id':subobj.stripeCustomerId}
            else:
                temp = stripe.Customer.create(
                    email=request.user.email,
                    name=request.user.username,
                )

            try:
                if period == 'Monthly':
                    pricekey = settings.STRIPE_DPM
                else:
                    pricekey = settings.STRIPE_DPY

                # if settings.ENVIRONMENT == 'local': ### dev stripe, this is fake money
                #     if period == 'Monthly':
                #         price_key = 
                #     else:
                #         price_key = 
                # elif settings.ENVIRONMENT == 'dev': ### prod stripe, this is real money
                #     if period == 'Monthly':
                #         price_key = 
                #     else:
                #         price_key =
                # else: ### prod stripe, this is real money
                #     if period == 'Monthly':
                #         price_key = 
                #     else:
                #         price_key =
            except Exception as e:
                print(e) 


            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?num='+str(num)+'&per='+str(per)+'&session_id='+str(profile_id)+'&session_id2={CHECKOUT_SESSION_ID}'
                , cancel_url=domain_url + 'canceled/'
                , payment_method_types=['card']
                , customer=temp['id']
                , mode='subscription'
                , allow_promotion_codes=True
                , line_items=[
                    {
                        'price': pricekey
                        , 'quantity': 1
                        , 'description':'Adding user "{}" to your pool'.format(profileobj.user.username)
                    }
                ]
                , metadata={
                    'invoice_description':'Initiated subscription'
                }
            )

            template = 'payments/create-checkout-session.html'
            context = {'sessionId' : checkout_session['id']}
            print('checkout_session', checkout_session)
            return render(request,template,context)
           
        except Exception as e:
            return JsonResponse({
                'error': str(e)
                , 'price': str(profileobj)
                , 'chargeAmount': str(find_charge_amount(profileobj, per))
                })

def success(request):
    # print('request', request)

    profileobj = profilemodel.objects.get(pk=int(request.GET['session_id']))
    # print('profileobj', profileobj)

    profileobj.is_paid_for = True
    profileobj.save()
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        temp = stripe.checkout.Session.retrieve(request.GET['session_id2'])
        # print('temp', temp)

        profileobj = profilemodel.objects.get(user=request.user)
        subobj = find_sub_obj(profileobj)
        subobj.stripeCustomerId = temp['customer']
        subobj.active = True
        if request.GET['per'] == 'm':
            if request.GET['num'] in ('1','2'):
                pricekey = settings.STRIPE_DM
                subobj.subtype = 'Data'
            else:
                pricekey = settings.STRIPE_DPM
                subobj.subtype = 'Data+Predictions'
            subobj.periodtype = 'Monthly'
            subobj.start_date = date.today()
            anchor = datetime.now() + timedelta(days=31)
        else:
            if request.GET['num'] in ('1','2'):
                pricekey = settings.STRIPE_DY
                subobj.subtype = 'Data'
            else:
                pricekey = settings.STRIPE_DPY
                subobj.subtype = 'Data+Predictions'

            subobj.periodtype = 'Annually'
            subobj.start_date = date.today()
            anchor = datetime.now() + timedelta(days=365)

        # print('pricekey', pricekey)
        # print('subobj.userpoolobj.users.count()', subobj.userpoolobj.users.count())
        # print("temp['customer']", temp['customer'])

        subobj.next_date = date(anchor.year, anchor.month, anchor.day)

        subobj.stripeSubscriptionId = temp['subscription']
        subobj.save()

        return redirect('/datasets')
    except Exception as e:
        print(e)
        subobj = find_sub_obj(profileobj)
        subid = subobj.stripeSubscriptionId
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.Subscription.modify(
            subid
            , quantity=subobj.userpoolobj.users.count()
            , proration_behavior='none'
        )

        userobj = User.objects.get(id=profileobj.user_id)

        if settings.DEBUG == True:
            html_message = render_to_string('email/confirm_account.html',{'link':'http://{}/verify/account/{}'.format(request.get_host(),profileobj.verification_key)})
        else:
            html_message = render_to_string('email/confirm_account.html',{'link':'https://{}/verify/account/{}'.format(request.get_host(),profileobj.verification_key)})
        plain_message = strip_tags(html_message)
        mail.send_mail(
            subject='Verify your account.',
            message=plain_message,
            html_message=html_message,
            recipient_list=[userobj.email],
            from_email='support@superloud.com',
            fail_silently=True
        )
        profileobj.is_paid_for = True
        profileobj.save()

        return redirect('/user-list')  

@login_required(login_url="/login/")
def canceled(request):
    template = 'payments/canceled.html'
    context = {}
    obj = profilemodel.objects.get(user=request.user)
    context['obj'] = obj
    subobj = find_sub_obj(obj)
    context['subobj'] = subobj

    try:
        poolobj = userpool.objects.get(user=obj)
    except:
        poolobjs = userpool.objects.all()
        for i in poolobjs:
            if obj in i.users.all():
                poolobj = i
                break

    poolobjs = poolobj.users.all()
    for i in poolobjs:
        if i.is_paid_for == False:
            temp = i.user
            temp.delete()

    return render(request,template,context)

@login_required(login_url="/login/")
def error(request):
    template = 'payments/error.html'
    context = {}
    obj = profilemodel.objects.get(user=request.user)
    context['obj'] = obj
    subobj = find_sub_obj(obj)
    context['subobj'] = subobj
    
    return render(request,template,context)

def transactions(request):
    template = 'payments/transactions.html'
    context = {'segment':'transaction'}
    obj = profilemodel.objects.get(user=request.user)
    context['obj'] = obj
    subobj = find_sub_obj(obj)
    context['subobj'] = subobj

    # if obj.is_admin == False or subobj.active == False:
    if obj.is_admin == False:
        return render(request,'accounts/access-denied.html')
    if not obj.verified:
        return redirect('/not-verified')

    stripe.api_key = settings.STRIPE_SECRET_KEY
    if subobj.stripeCustomerId:
        all_transactions = stripe.PaymentIntent.list(customer=subobj.stripeCustomerId, limit=100)

        # Getting upcoming transactions if they exist
        try:
            upcoming_transactions = stripe.Invoice.upcoming(customer=subobj.stripeCustomerId)
            upcoming_transactions['amount_due'] = upcoming_transactions['amount_due']/100
            upcoming_transactions['start'] = datetime.utcfromtimestamp(upcoming_transactions['period_start']).strftime('%B %d %Y')
            upcoming_transactions['end'] = datetime.utcfromtimestamp(upcoming_transactions['period_end']).strftime('%B %d %Y')
            context['upcoming'] = upcoming_transactions
        except:
            context['upcoming'] = []

        # Getting credit amount from downgrading (if exists)
        try:
            customer_details = stripe.Customer.retrieve(id=subobj.stripeCustomerId)
            context['balance'] = -1 * customer_details['balance']/100
        except:
            context['balance'] = 0

        context['retval'] = find_relevant_transactions(all_transactions, subobj.stripeSubscriptionId)
    else:
        context['retval'] = []

    return render(request,template,context)

def find_relevant_transactions(b, subid):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    retval = []

    try:
        current_subscription = stripe.Subscription.retrieve(subid)

        for key in json.loads(str(current_subscription.metadata)):
            deleted_user = json.loads(current_subscription.metadata[key].replace("'",'"'))
            deleted_user['start_epoch'] = deleted_user['deleted_at']

            deleted_user['desc'] = "Deleted user \"" + deleted_user['username'] + "\""
            deleted_user['start'] = datetime.utcfromtimestamp(deleted_user['deleted_at']).strftime('%B %d %Y')
            if deleted_user['subtype'] == 'Data+Predictions':
                deleted_user['id'] = 'Deleted user enrolled in upgraded tier paid ' + deleted_user['periodtype']
            
            retval.append(deleted_user)
    except:
        pass

    try:
        for i in b['data']:
            obj = {}
            count = 1
            obj['num'] = count
            if i['invoice'] is not None:
                i = stripe.Invoice.retrieve(i['invoice'])
                try:
                    obj['desc2'] = "Initiated new subscription"
                except:
                    obj['desc'] = i['metadata']['invoice_description']
                obj['start'] = datetime.utcfromtimestamp(i['period_start']).strftime('%B %d %Y')
                obj['end'] = datetime.utcfromtimestamp(i['period_end']).strftime('%B %d %Y')
                obj['start_epoch'] = datetime.utcfromtimestamp(i['period_start']).timestamp()
                obj['end_epoch'] = datetime.utcfromtimestamp(i['period_end']).timestamp()
                obj['total'] = i['amount_due']/100
                obj['status'] = i['status']
                obj['id'] = i['hosted_invoice_url']
                retval.append(obj)
            else:
                if len(i["charges"]["data"]) > 0:
                    try:
                        obj['desc2'] = i['metadata']['invoice_description']
                    except:
                        obj['desc'] = "Added User to plan"
                    obj['total'] = i['amount']/100
                    obj['start'] = datetime.utcfromtimestamp(i['created']).strftime('%B %d %Y')
                    obj['end'] = obj['start']
                    obj['start_epoch'] = datetime.utcfromtimestamp(i['created']).timestamp()
                    obj['end_epoch'] = obj['start']
                    if i['status'] == "succeeded":
                        obj['status'] = "paid"
                    else:
                        obj['status'] = i['status']
                    obj['id'] = i["charges"]["data"][0]["receipt_url"]
                    retval.append(obj)
                else:
                    pass
    except:
        pass

    ### Sort the list of invoices and values by time they happened
    retval.sort(key=lambda x: x['start_epoch'])
    return retval[::-1]


def cancel_subscription(request):
    template = 'payments/delete-sub.html'
    context = {'segment':'delete-sub'}

    if request.method == 'GET':
        try:
            profile_id = request.GET['profile-id']
            subtype = request.GET['subtype']
            pertype = request.GET['pertype']
            periodchoice = request.GET['periodchoice']
        except:
            return redirect('/error')

    profileobj = profilemodel.objects.get(pk = profile_id)
    if profileobj.is_admin == False:
        return render(request,'accounts/access-denied.html')
    if not profileobj.verified:
        return redirect('/not-verified')
    subobj = find_sub_obj(profileobj)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    temp = stripe.Subscription.modify(
        subobj.stripeSubscriptionId
        , cancel_at_period_end=True
    )
    try:
        subobj.cancel_at = datetime.utcfromtimestamp(temp.cancel_at)
        subobj.canceled_at = datetime.utcfromtimestamp(temp.canceled_at)
        subobj.save()
    except:
        pass

    context['obj'] = profileobj
    context['subobj'] = subobj
    return render(request, template, context)



def switch_billing_period(request):
    template = 'payments/billing_period_switched.html'
    context = {'segment':'billing_period_switched'}

    ### Switch from monthly to annually, and from annually to monthly
    ### https://stripe.com/docs/billing/subscriptions/upgrade-downgrade
    if request.method == 'GET':
        try:
            profile_id = request.GET['profile-id']
            subtype = request.GET['subtype']
            pertype = request.GET['pertype']
            periodchoice = request.GET['periodchoice']
        except:
            return redirect('/error')
        if settings.DEBUG == True:
            domain_url = 'http://{}/'.format(request.get_host())
        else:
            domain_url = 'https://{}/'.format(request.get_host())
        stripe.api_key = settings.STRIPE_SECRET_KEY

        profileobj = profilemodel.objects.get(pk = profile_id)
        if profileobj.is_admin == False:
            return render(request,'accounts/access-denied.html')
        if not profileobj.verified:
            return redirect('/not-verified')
        subobj = find_sub_obj(profileobj)

        temp = stripe.Subscription.retrieve(
            subobj.stripeSubscriptionId
        )

        prorated_dates = datetime.utcfromtimestamp(temp.current_period_end) - datetime.utcnow()

        if pertype == 'Monthly':
            pricekey = settings.STRIPE_DPY
            subobj.subtype = 'Data+Predictions'
            subobj.periodtype = 'Annually'
            subobj.start_date = datetime.utcfromtimestamp(temp.current_period_start)
            subobj.next_date = datetime.utcfromtimestamp(temp.current_period_end) + timedelta(days=366) - prorated_dates
            subobj.save()
        else:
            pricekey = settings.STRIPE_DPM
            subobj.subtype = 'Data+Predictions'
            subobj.periodtype = 'Monthly'
            subobj.start_date = datetime.utcfromtimestamp(temp.current_period_start)
            subobj.next_date = datetime.utcfromtimestamp(temp.current_period_end) + timedelta(days=31) - prorated_dates
            subobj.save()
           
        temp2 = stripe.Subscription.modify(
            subobj.stripeSubscriptionId
            , proration_behavior='always_invoice'
            , items=[{
                'id': temp['items']['data'][0]['id']
                , 'price': pricekey
                , 'quantity': subobj.userpoolobj.users.count()
            }]
        )

        context['obj'] = profileobj
        context['subobj'] = subobj
        return render(request, template, context)



def reinstate_subscription(request):
    template = 'payments/account_reinstated.html'
    context = {'segment':'account_reinstated'}

    ### Reinstate subscription OR change billing and reinstate
    ### https://stripe.com/docs/billing/subscriptions/cancel
    if request.method == 'GET':
        try:
            profile_id = request.GET['profile-id']
            subtype = request.GET['subtype']
            pertype = request.GET['pertype']
            periodchoice = request.GET['periodchoice']
        except:
            return redirect('/error')
        if settings.DEBUG == True:
            domain_url = 'http://{}/'.format(request.get_host())
        else:
            domain_url = 'https://{}/'.format(request.get_host())
        stripe.api_key = settings.STRIPE_SECRET_KEY

        profileobj = profilemodel.objects.get(pk = profile_id)
        if profileobj.is_admin == False:
            return render(request,'accounts/access-denied.html')
        if not profileobj.verified:
            return redirect('/not-verified')
        subobj = find_sub_obj(profileobj)

        temp = stripe.Subscription.retrieve(
            subobj.stripeSubscriptionId
        )

        prorated_dates = datetime.utcfromtimestamp(temp.current_period_end) - datetime.utcnow()

        if (pertype == 'Monthly' and periodchoice == 'Monthly') or (pertype == 'Annually' and periodchoice == 'Monthly'):
            pricekey = settings.STRIPE_DPM
            subobj.subtype = 'Data+Predictions'
            subobj.periodtype = 'Monthly'
            subobj.start_date = datetime.utcfromtimestamp(temp.current_period_start)
            subobj.next_date = datetime.utcfromtimestamp(temp.current_period_end) + timedelta(days=31) - prorated_dates
            subobj.save()
        else:
            pricekey = settings.STRIPE_DPY
            subobj.subtype = 'Data+Predictions'
            subobj.periodtype = 'Annually'
            subobj.start_date = datetime.utcfromtimestamp(temp.current_period_start)
            subobj.next_date = datetime.utcfromtimestamp(temp.current_period_end) + timedelta(days=366) - prorated_dates
            subobj.save()
           
        temp = stripe.Subscription.retrieve(
            subobj.stripeSubscriptionId
        )

        temp2 = stripe.Subscription.modify(
            subobj.stripeSubscriptionId
            , cancel_at_period_end=False
            , proration_behavior='always_invoice'
            , items=[{
                'id': temp['items']['data'][0]['id']
                , 'price': pricekey
                , 'quantity': subobj.userpoolobj.users.count()
            }]
        )

        try:
            subobj.cancel_at = None
            subobj.canceled_at = None
            subobj.save()
        except:
            pass

        context['obj'] = profileobj
        context['subobj'] = subobj
        return render(request, template, context)


# https://docs.djangoproject.com/en/4.0/ref/contrib/auth/#django.contrib.auth.signals.user_logged_in
# https://docs.djangoproject.com/en/4.0/topics/signals/
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # print('user {} logged in through page {}'.format(user.username, request.META.get('HTTP_REFERER')))
    
    try:
        ### Get the current object that saved in the DB
        subobj = find_sub_obj(profilemodel.objects.get(user=request.user))

        ### Get the Stripe subscription associated with the account
        stripe.api_key = settings.STRIPE_SECRET_KEY
        temp = stripe.Subscription.retrieve(
            subobj.stripeSubscriptionId
        )

        ### If the DB object is not the same as the stripe object, update and save the permissions.
        ### Stripe will be more up to date than the DB. The DB only changes when a subscription
        ### changes
        if temp.status == 'active':
            subobj.active = True
            subobj.save()
        else:
            subobj.active = False
            subobj.save()
    except:
        pass





