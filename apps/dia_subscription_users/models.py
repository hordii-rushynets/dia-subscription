from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


class Signer(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    vote = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'
