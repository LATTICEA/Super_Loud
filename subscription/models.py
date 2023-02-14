from django.db import models
from authentication.models import userpool

periodchoices = (
    ('Monthly','Monthly'),
    ('Annually','Annually'),
    ('Trial','Trial')
)

subchoices = (
    ('Data','Data'),
    ('Data+Predictions','Data+Predictions')
)

class subscription_details(models.Model):
    userpoolobj = models.ForeignKey(userpool,on_delete=models.SET_NULL, null=True, blank=True)
    periodtype = models.CharField(max_length=20,choices=periodchoices)
    subtype = models.CharField(max_length=20,choices=subchoices)
    start_date = models.DateField(null=True)
    next_date = models.DateField(null=True)
    trial_availed = models.BooleanField(default=False)
    amount_paid = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    stripeCustomerId = models.CharField(max_length=255,null=True, blank=True)
    stripeSubscriptionId = models.CharField(max_length=255,null=True, blank=True)
    cancel_at = models.DateField(null=True, blank=True)
    canceled_at = models.DateField(null=True, blank=True)

    def __str__(self):
        if self.active:
            a = 'Active'
        else:
            a = 'Deactivated'
        return '{} - {}'.format(self.periodtype,a)