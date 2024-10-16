from django.db import models


class Company(models.Model):
    BUSSINES_TYPES = (
        ('small', 'small'),
        ('veterans', 'veterans')
    )

    business_type = models.CharField(max_length=15, choices=BUSSINES_TYPES, default=BUSSINES_TYPES[0][0])
    name = models.CharField(max_length=255)
    image = models.FileField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}'


class Signer(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    vote_business = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, related_name='vote_business')
    vote_business_veterans = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, related_name='vote_business_veterans')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'
