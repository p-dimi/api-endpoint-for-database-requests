from django.db import models

# Create your models here.
# model based on db structure provided in task

class ClicksInfo(models.Model):
    # format should not exceed yyyy-mm-dd format, but max_length has a few extra chars for leeway
    date = models.CharField(max_length = 15)
    
    # allowing 50 chars in case of long channel names
    channel = models.CharField(max_length = 50)
    
    # country code is 2 chars (GB, US, DE, FR etc)
    country = models.CharField(max_length = 2)
    
    # 10 max chars in case of windows 10 (10 chars)
    os = models.CharField(max_length = 10)
    
    # 50 chars max
    impressions = models.CharField(max_length = 50)
    clicks = models.CharField(max_length = 50)
    installs = models.CharField(max_length = 50)
    spend = models.CharField(max_length = 50)
    revenue = models.CharField(max_length = 50)
    
    # cpi insert
    cpi = models.CharField(max_length = 50, default='0')
    
    def __str__(self):
        return self.date