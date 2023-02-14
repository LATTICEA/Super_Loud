# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(User, UserAdmin)
admin.site.register(profilemodel)
admin.site.register(userpool)