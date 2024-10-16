from functools import cache
from typing import OrderedDict

from rest_framework import exceptions, serializers

from apps.dia_subscription_users import models


class CompanySerializer(serializers.ModelSerializer):
    signer_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Company
        fields = ['id', 'business_type', 'name', 'image', 'description', 'signer_count']
    
    def get_signer_count(self, obj):
        return models.Signer.objects.filter(vote_business=obj).count() + models.Signer.objects.filter(vote_business_veterans=obj).count()



class SignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Signer
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'vote_business', 'vote_business_veterans']
    
    def validate(self, attrs: OrderedDict) -> OrderedDict:
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        middle_name = attrs.get('middle_name')

        if not all([first_name, last_name, middle_name]):
            error_msg = f'Missing user data: First name: {first_name}, Last name: {last_name}, Middle name: {middle_name}'
            print('Error:', error_msg)
            raise exceptions.ValidationError(error_msg)

        if models.Signer.objects.filter(first_name=first_name, last_name=last_name,
                                         middle_name=middle_name, vote_business__isnull=False,
                                         vote_business_veterans__isnull=False).exists():
            error_msg = 'Vote already exists.'
            print('Error:', error_msg)
            raise exceptions.ValidationError('Vote already exists.')
        
        return attrs
