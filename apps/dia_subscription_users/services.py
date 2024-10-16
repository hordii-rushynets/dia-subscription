"""Service to validate subscription."""
import os
import uuid
import json
import requests
from .eusign import EUSign
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.core.cache import cache



class DIASubscriptionService:
    CAS = f'{settings.DIA_CERTIFICATES_ROOT}/{settings.CAS_FILE_NAME}'
    CA_CERTIFICATES = f'{settings.DIA_CERTIFICATES_ROOT}/{settings.CA_CERTIFICATES_FILE_NAME}'

    def __init__(self):
        self.eu_sign = EUSign()

        try:
            self.eu_sign.initialize(self.CAS, self.CA_CERTIFICATES)
        except Exception as e:
            print ("Initialize crypto library failed. " + str(e))
            raise ValidationError("Can't initialize EUSign.")

    def get_acquirer_token(self):
        response = requests.get(f'{settings.DIA_BASE_URL}api/v1/auth/acquirer/{settings.DIA_ACQUIRER_TOKEN}',
                                headers={'Authorization': f'Basic {settings.DIA_AUTH_ACQUIRER_TOKEN}'})
        
        if not response.status_code == 200:
            raise ValidationError('Filed to get acquirer.')
        
        return response.json().get('token')

    def create_branch(self, token: str) -> str:
        response = requests.post(f'{settings.DIA_BASE_URL}api/v2/acquirers/branch', data=json.dumps({
            "name": "УП медіа плюс",
            "email": "v.vitalii.pustovoit@pravda.ua",
            "region": "Kиївська обл.",
            "location": "м. Київ",
            "deliveryTypes": ["api"],
            "offerRequestType": "dynamic",
            "street": "вул. Жилянська",
            "house": "48/50а",
            "scopes": {"diiaId": ["auth"]}
        }), headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        if not response.status_code == 200:
            raise ValidationError('Filed to create branch.')
        
        return response.json().get('_id')

    def create_branch_offer(self, token: str, branch_id: str) -> str:
        response = requests.post(f'{settings.DIA_BASE_URL}api/v1/acquirers/branch/{branch_id}/offer', data=json.dumps({
            "name": "Авторизація",
            "scopes": { 
                "diiaId": ["auth"]
            }
        }), headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        if not response.status_code == 200:
            raise ValidationError('Filed to create branch offer.')

        return response.json().get('_id')

    def make_offer_request(self, token: str, branch_id: str, offer_id: str, vote_business_id: int, vote_business_veterans_id: int) -> str:
        request_uuid: uuid.UUID = uuid.uuid4()
        request_id: bytes = self.get_hash(request_uuid.bytes).decode('utf-8')
        
        response = requests.post(f'{settings.DIA_BASE_URL}/api/v2/acquirers/branch/{branch_id}/offer-request/dynamic', data=json.dumps({
            "offerId": f"{offer_id}",
            "returnLink": f"https://dia-subscription.test-internet-technology-hub.online/api/v1/validate-sign?requestId={request_id}",
            "requestId": request_id,
            "signAlgo": "DSTU",
            "scopes": {"diiaId": ["auth"]}
        }), headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        if not response.status_code == 200:
            raise ValidationError('Failed to make offer request.')
        
        cache.set(f'{request_id}_vote_business_id', vote_business_id, timeout=60*4)
        cache.set(f'{request_id}_vote_business_veterans_id', vote_business_veterans_id, timeout=60*4)
        cache.set(request_id, request_uuid, timeout=60*4)
        return response.json().get('deeplink')

    def get_user_data(self, signature: str, request_id: str) -> dict:
        data_file_path = f"{os.getcwd()}.ext.cades-x-long"
        sign_file_path = f"{os.getcwd()}.ext.cades-x-long.p7s"

        print(f'Signature: {signature} \n')
        print(f'RequestId from request: {request_id} \n\n')

        request_uuid: uuid.UUID = cache.get(request_id)
        print('request uuid', request_uuid, '\n')

        new_signature = self.eu_sign.cades_make_container(signature, None, self.eu_sign.SIGN_TYPE_CADES_X_LONG)
        results = self.eu_sign.cades_verify_data(request_uuid.bytes, new_signature)
        self.eu_sign.print_verify_results(data_file_path, sign_file_path, results)
        signer = results[0]["infoEx"]["pszSubjCN"].split(' ')

        return {
            'first_name': signer[0],
            'last_name': signer[1],
            'middle_name': signer[2],
            'vote_business': int(cache.get(f'{request_id}_vote_business_id')),
            'vote_business_veterans': int(cache.get(f'{request_id}_vote_business_veterans_id')),
        }

    def get_hash(self, request_uuid: bytes) -> bytes:
        try:
            return self.eu_sign.hash_data(request_uuid)
        except Exception as e:
            print ("Hash data failed. " + str(e))
            
    

