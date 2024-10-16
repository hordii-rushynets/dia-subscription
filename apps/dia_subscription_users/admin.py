from django.contrib import admin

from apps.dia_subscription_users import models


class CompanyAdmin(admin.ModelAdmin):
    # Define a method to count related signers
    def signer_count(self, obj):
        return models.Signer.objects.filter(vote_business=obj).count() + models.Signer.objects.filter(vote_business_veterans=obj).count()

    signer_count.short_description = 'Signer Count'
    list_display = ('name', 'business_type', 'signer_count')

admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.Signer)
