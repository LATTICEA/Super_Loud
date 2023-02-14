# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

#from datasetapp.models import wage_county_raw

class User(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    )
    email = models.EmailField(_('email address'), blank=True, unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class profilemodel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    verified = models.BooleanField(default=False)
    verification_key = models.CharField(max_length=25)
    reset_key = models.CharField(max_length=25)
    birthday = models.CharField(max_length=100,null=True)
    gender = models.CharField(max_length=10,default='gender')
    phone = models.CharField(max_length=15,default='',blank=True)
    address = models.CharField(max_length=500,default=' ')
    no = models.IntegerField(null=True,blank=True)
    city = models.CharField(max_length=100,default='',blank=True)
    state = models.CharField(max_length=100,default='State')
    zip_code = models.IntegerField(null=True,blank=True)
    profile_pic = models.ImageField(null=True)
    cover_pic = models.ImageField(null=True)
    comp_news = models.BooleanField(default=False)
    account_act = models.BooleanField(default=False)
    meetups = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    is_tester = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)

    is_paid_for = models.BooleanField(default=False)

    def __str__(self):
        return "Profile Model - {}".format(self.id)

class userpool(models.Model):
    user = models.ForeignKey(profilemodel,on_delete=models.SET_NULL,null=True ,related_name='userprof')
    users = models.ManyToManyField(profilemodel,related_name='usersprof')

    def __str__(self):
        return "User pool - {}".format(self.id)


from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None