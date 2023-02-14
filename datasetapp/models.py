from django.db import models
from authentication.models import User
from .dbreqs import *


class datasetmodel(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    settype = models.CharField(max_length=10, default='county')
    name = models.CharField(max_length=200)
    area_fips = models.CharField(max_length=400)
    industry_code = models.CharField(max_length=400)
    state_code = models.CharField(max_length=400)
    occupation_code  = models.CharField(max_length=400, default=' ')
    area_title = models.CharField(max_length=400, default=' ')
    industry_title = models.CharField(max_length=400, default=' ')
    state_title = models.CharField(max_length=400, default=' ')
    occupation_title = models.CharField(max_length=400, default=' ')
    skills = models.CharField(max_length=1, default=' ', blank=True, null=True)
    dataset_id = models.CharField(max_length=30, default='', blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.id)