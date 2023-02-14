# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include  # add this


urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path("", include("authentication.urls")), # Auth routes - login / register
    path("", include("datasetapp.urls")),
    path("", include("subscription.urls")),
    path("", include("payments.urls")),
    path("", include("app.urls")),             # UI Kits Html files
]

