from django.contrib import admin 
from apps.dia_subscription_users import models

admin.site.register(models.Company)
admin.site.register(models.Signer)

