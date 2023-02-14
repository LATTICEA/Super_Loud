# -*- encoding: utf-8 -*-

from django.contrib import auth
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.forms.utils import ErrorList
from django.http import HttpResponse
import stripe
from .forms import LoginForm, SignUpForm
from .models import profilemodel, userpool, User
from datasetapp.models import datasetmodel
from django.core.mail import EmailMessage
from django.core.mail import send_mail

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.contrib.auth.decorators import login_required
import random
from datetime import datetime
from django.http import JsonResponse
import json

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.core.files.storage import FileSystemStorage

from subscription.models import subscription_details
from subscription.views import find_sub_obj
from django.conf import settings

def validateEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
             
            username = form.cleaned_data.get("email").lower()
            password = form.cleaned_data.get("password")
            user = authenticate(
                request=request ### https://github.com/jazzband/django-axes/blob/master/docs/3_usage.rst
                , username=username
                , password=password
            )
            if user is not None:
                login(request, user)
                return redirect("/datasets")
            else:    
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'    

    return render(request, "accounts/login.html", {"form": form, "msg" : msg})

def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("email").lower()
            objs = User.objects.filter(email=username)
            if len(objs) != 0:
                msg = 'User with that email already exists!'
            else:
                form.save()
                raw_password = form.cleaned_data.get("password1")
                user = authenticate(
                    request=request ### https://github.com/jazzband/django-axes/blob/master/docs/3_usage.rst
                    , username=username
                    , password=raw_password
                )
                obj = profilemodel()
                obj.user = user
                obj.verification_key = gen_key()
                obj.is_admin = True
                obj.is_superadmin = True
                obj.is_paid_for = True
                obj.save()
                if settings.DEBUG == True:
                    html_message = render_to_string('email/confirm_account.html',{'link':'http://{}/verify/account/{}'.format(request.get_host(),obj.verification_key)})
                else:
                    html_message = render_to_string('email/confirm_account.html',{'link':'https://{}/verify/account/{}'.format(request.get_host(),obj.verification_key)})
                plain_message = strip_tags(html_message)
                mail.send_mail(
                    subject='Verify your account.',
                    message=plain_message,
                    html_message=html_message,
                    recipient_list=[user.email],
                    from_email='support@superloud.com',
                    fail_silently=True
                )
                poolobj = userpool()
                poolobj.user = obj
                poolobj.save()
                poolobj.users.add(obj)
                poolobj.save()

                # if settings.DEBUG:
                #     stripe.api_key = settings.STRIPE_SECRET_KEY
                #     stripe.Customer.create(
                #         email = user.email
                #         , payment_method = "pm_card_visa"
                #     )
                # else:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe.Customer.create(
                    email = user.email
                    # payment_method = "pm_card_visa",
                )

                subobj = subscription_details()
                subobj.userpoolobj = poolobj
                subobj.periodtype = 'Trial'
                subobj.subtype = 'Data'
                subobj.save()
                login(request,user)
                return redirect("/not-verified")
        else:
            msg = 'Form is not valid'    
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })

def gen_key():
    a = '1234567890qwertyuioplkjhgfdsazxcvbnm'
    retval = ''
    for i in range(25):
        retval += a[random.randint(0,len(a)-1)]
    return retval

def verify_user(request,verkey):
    try:
        obj = profilemodel.objects.get(verification_key=verkey)
        obj.verification_key = 'empty'
        obj.verified = True
        obj.save()
        return redirect('/datasets')
    except:
        return redirect('/register/')

@login_required(login_url="/login/")
def not_verified(request):
    template = 'accounts/not-verified.html'
    context = {}
    return render(request,template,context)

@login_required(login_url="/login/")
def not_subscribed(request):
    context = {}

    context['obj'] = profilemodel.objects.get(user=request.user)
    context['subobj'] = find_sub_obj(context['obj'])

    #template = 'accounts/not-subscribed.html'
    template = 'dataset/superloud_template.html'
    return render(request,template,context)

def reset1(request):
    template = 'accounts/page-forgot-password.html'
    context = {'message':False}
    if request.method == 'POST':
        a = request.POST['email'].lower()
        try:
            obj = profilemodel.objects.get(user__email = a)
        except:
            context['thismessage'] = 'No account exists with that email address. Please check again!'
            return render(request,template,context)
        if obj.verified == False:
            return redirect('/not-verified')
        obj.reset_key = gen_key()
        obj.save()
        if settings.DEBUG == True:
            html_message = render_to_string('email/reset_password.html',{'link':'http://{}/reset/account-password/{}'.format(request.get_host(),obj.reset_key)})
        else:
            html_message = render_to_string('email/reset_password.html',{'link':'https://{}/reset/account-password/{}'.format(request.get_host(),obj.reset_key)})
        plain_message = strip_tags(html_message)
        mail.send_mail(
            subject='Reset your password.',
            message=plain_message,
            html_message=html_message,
            recipient_list=[obj.user.email],
            from_email='support@superloud.com',
            fail_silently=True
        )
        context['message'] = True
    return render(request,template,context)

def reset2(request,resetkey):
    template = 'accounts/page-reset-password.html'
    context = {}
    obj = profilemodel.objects.get(reset_key=resetkey)
    if request.method == 'POST':
        a = request.POST['pass']
        b = request.POST['pass1']
        if a == b:
            obj.user.set_password(a)
            obj.user.save()
            return redirect('/login/')
        else:
            context['message'] = 'The passwords do not match!'
    return render(request,template,context)

@login_required(login_url="/login/")
def profile_page(request):
    template = 'accounts/settings.html'
    context = {}
    obj = profilemodel.objects.get(user=request.user)
    if obj.verified:
        pass
    else:
        return redirect('/not-verified')
    if obj.is_suspended:
        return redirect('/account-suspended')
    context['obj'] = obj
    if request.method == 'POST':
        userobj = request.user
        userobj.first_name = request.POST['first_name']
        userobj.last_name = request.POST['last_name']
        userobj.save()
        obj.birthday = request.POST['bday']
        obj.gender = request.POST['gender']
        obj.phone = request.POST['phone']
        obj.address = request.POST['address']
        obj.no = request.POST['no']
        obj.city = request.POST['city']
        obj.state = request.POST['state']
        obj.zip_code = request.POST['zip']
        if 'comp_news' in request.POST.keys():
            obj.comp_news = True
        if 'account_act' in request.POST.keys():
            obj.account_act = True
        if 'meetups' in request.POST.keys():
            obj.meetups = True
        obj.save()
    context['segment'] = 'settings'
    return render(request,template,context)

@login_required(login_url="/login/")
def profile_pic_change(request):
    a = profilemodel.objects.get(user=request.user)
    image = request.FILES['pic']
    fs = FileSystemStorage()
    filename = fs.save(image.name, image)
    a.profile_pic = fs.url(filename)
    a.save()
    return redirect('/profile-page')

@login_required(login_url="/login/")
def cover_pic_change(request):
    a = profilemodel.objects.get(user=request.user)
    image = request.FILES['pic']
    fs = FileSystemStorage()
    filename = fs.save(image.name, image)
    a.cover_pic = fs.url(filename)
    a.save()
    return redirect('/profile-page')

@login_required(login_url="/login/")
def user_list(request):
    template = 'accounts/users.html'
    context = {'segment':'users'}
    obj = profilemodel.objects.get(user=request.user)
    subobj = find_sub_obj(obj)
    try:
        poolobj = userpool.objects.get(user=obj)
    except:
        poolobjs = userpool.objects.all()
        for i in poolobjs:
            if obj in i.users.all():
                poolobj = i
                break
    if obj.is_admin == False or subobj.active is None:
        return render(request,'accounts/access-denied.html')
    if not obj.verified:
        return redirect('/not-verified')
    # if subobj.active == False:
    #     return render(request,'subs/not-subscribed.html',{'obj':obj})
    if request.method == 'POST': ### this means a form was submitted
        if request.POST['formtype'] == 'a':
            if request.POST['password'] == request.POST['password2']:
                if validateEmail(email=request.POST['email']):
                    if len(User.objects.filter(email=request.POST['email'])) == 0:
                        if check_username_in_pool(request.POST['username'],poolobj):
                            if subobj.periodtype == 'Trial':
                                userobj = User()
                                userobj.username = request.POST['username']
                                userobj.email = request.POST['email']
                                userobj.set_password(request.POST['password'])
                                userobj.save()
                                obj2 = profilemodel()
                                obj2.user = userobj
                                obj2.verification_key = gen_key()
                                obj2.save()
                                if settings.DEBUG == True:
                                    html_message = render_to_string('email/confirm_account.html',{'link':'http://{}/verify/account/{}'.format(request.get_host(),obj2.verification_key)})
                                else:
                                    html_message = render_to_string('email/confirm_account.html',{'link':'https://{}/verify/account/{}'.format(request.get_host(),obj2.verification_key)})
                                plain_message = strip_tags(html_message)
                                mail.send_mail(
                                    subject='Verify your account.',
                                    message=plain_message,
                                    html_message=html_message,
                                    recipient_list=[userobj.email],
                                    from_email='support@superloud.com',
                                    fail_silently=True
                                )
                                poolobj.users.add(obj2)
                                poolobj.save()
                                obj2.is_paid_for = True
                                obj2.save()
                            else:
                                userobj = User()
                                userobj.username = request.POST['username']
                                userobj.email = request.POST['email']
                                userobj.set_password(request.POST['password'])
                                userobj.save()
                                obj2 = profilemodel()
                                obj2.user = userobj
                                obj2.verification_key = gen_key()
                                obj2.save()
                                # html_message = render_to_string('email/confirm_account.html',{'link':'https://{}/verify/account/{}'.format(request.get_host(),obj2.verification_key)})
                                # plain_message = strip_tags(html_message)
                                # mail.send_mail(
                                #     subject='Verify your account.',
                                #     message=plain_message,
                                #     html_message=html_message,
                                #     recipient_list=[userobj.email],
                                #     from_email='support@superloud.com',
                                #     fail_silently=True
                                # )
                                poolobj.users.add(obj2)
                                poolobj.save()
                                # obj2.is_paid_for = True
                                # obj2.save()
                                return redirect('/create-checkout-session?profile-id={}'.format(obj2.id))
                        else:
                            context['message'] = 'Username is already taken'
                    else:
                        context['message'] = 'Email is already taken'
                else:
                    context['message'] = 'Email address is not valid'
            else:
                context['message'] = 'Entered passwords do not match'
        else:
            try:
                context['retid'] = request.POST['id']
                selobj = profilemodel.objects.get(pk=request.POST['id'])
                usersobjcheck = User.objects.filter(email=request.POST['email'].lower())
                if len(usersobjcheck) == 0:
                    seluserobj = selobj.user
                    seluserobj.email = request.POST['email'].lower()
                    selobj.verified = False
                    selobj.verification_key = gen_key()
                    if settings.DEBUG == True:
                        html_message = render_to_string('email/confirm_account.html',{'link':'http://{}/verify/account/{}'.format(request.get_host(),selobj.verification_key)})
                    else:
                        html_message = render_to_string('email/confirm_account.html',{'link':'https://{}/verify/account/{}'.format(request.get_host(),selobj.verification_key)})
                    plain_message = strip_tags(html_message)
                    mail.send_mail(
                        subject='Verify your account.',
                        message=plain_message,
                        html_message=html_message,
                        recipient_list=[seluserobj.email],
                        from_email='support@superloud.com',
                        fail_silently=True
                    )
                    selobj.save()
                    seluserobj.save()
                else:
                    context['message2'] = "The entered email is not available."
            except Exception as e:
                context['message2'] = "Your request could not be processed."
            
    
    context['obj'] = obj
    context['subobj'] = subobj
    poolobjs = poolobj.users.all()
    for i in poolobjs:
        if i.is_paid_for == False:
            temp = i.user
            temp.delete()
    context['objs'] = poolobj.users.all()
    return render(request,template,context)

def delete_user(request,id):
    userobj = User.objects.get(pk=id)
    profileobj = profilemodel.objects.get(user=request.user)
    subobj = find_sub_obj(profileobj)

    username = userobj.username
    email = userobj.email
    created_at = userobj.date_joined
    subtype = subobj.subtype
    periodtype = subobj.periodtype

    deleted_user = {
        'email': str(datetime.now().timestamp())
        , 'user_data': {
            'email': userobj.email
            , 'username': userobj.username
            , 'created_at': created_at.timestamp()
            , 'deleted_at': datetime.now().timestamp()
            , 'subtype': subobj.subtype
            , 'periodtype': subobj.periodtype
        }
    }

    stripe.api_key = settings.STRIPE_SECRET_KEY
    userobj.delete()

    try:
        temp = stripe.Subscription.modify(
            subobj.stripeSubscriptionId
            , quantity = subobj.userpoolobj.users.count()
            , proration_behavior='none'
            , metadata = {
                deleted_user['email']: str(deleted_user['user_data'])
            }
        )
    except:
        pass

    return redirect('/user-list')

def suspend_user(request,id):
    obj = profilemodel.objects.get(pk=id)
    if obj.is_suspended:
        obj.is_suspended = False
    else:
        obj.is_suspended = True
    obj.save()
    return redirect('/user-list')

def view_details(request,id):
    template = 'accounts/details.html'
    context = {}
    obj = profilemodel.objects.get(user=request.user)
    context['obj'] = obj
    detailobj = profilemodel.objects.get(pk=id)
    context['detailobj'] = detailobj
    dataobjs = datasetmodel.objects.filter(user=detailobj.user)
    context['dataobjs'] = dataobjs
    return render(request,template,context)

def make_admin(request,id):
    obj = profilemodel.objects.get(pk=id)
    if obj.is_admin:
        obj.is_admin = False
    else:
        obj.is_admin = True
    obj.save()
    return redirect('/user-list')

def account_suspended(request):
    template = 'accounts/suspended.html'
    return render(request,template)

def delete_account(request):
    obj = profilemodel.objects.get(user=request.user)
    subobj = find_sub_obj(obj)
    context = {}
    context['obj'] = obj
    context['subobj'] = subobj
    if obj.verified and obj.is_superadmin:
        template = 'delete-account.html'
        return render(request,template,context)
    else:
        return render(request,'accounts/access-denied.html')

def delete_account_completely(request,id):
    if str(request.user.id) == str(id):
        obj = profilemodel.objects.get(user=request.user)
        subobj = find_sub_obj(obj)

        auth.logout(request)
        try:
            poolobj = userpool.objects.get(user=obj)
        except:
            poolobjs = userpool.objects.all()
            for i in poolobjs:
                if obj in i.users.all():
                    poolobj = i
                    break
        for i in poolobj.users.all():
            i.user.delete()
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if subobj.stripeSubscriptionId:
        temp = stripe.Subscription.delete(
            subobj.stripeSubscriptionId
        )
    else:
        pass
    return redirect('/')

def check_username_in_pool(username,poolobj):
    for i in poolobj.users.all():
        if username == i.user.username:
            return False
    return True