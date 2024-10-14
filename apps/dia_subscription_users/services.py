"""Service to validate subscription."""
import os
from .eusign import EUSign
from django.conf import settings


class DIASubscriptionService:
    CAS = f'{settings.DIA_CERTIFICATES_ROOT}/{settings.CAS_FILE_NAME}'
    CA_CERTIFICATES = f'{settings.DIA_CERTIFICATES_ROOT}/{settings.CA_CERTIFICATES_FILE_NAME}'

    def __init__(self):
        self.eu_sign = EUSign()

    def get_user_data(self, signature: str, request_id: str):
        try:
            self.eu_sign.initialize(self.CAS, self.CA_CERTIFICATES)
        except Exception as e:
            print ("Initialize crypto library failed. " + str(e))
            return
        
        hash = self.get_hash(request_id)

        data_file_path = f"{os.getcwd()}.ext.cades-x-long"
        sign_file_path = f"{os.getcwd()}.ext.cades-x-long.p7s"

        new_signature = self.eu_sign.cades_make_container(signature, None, self.eu_sign.SIGN_TYPE_CADES_X_LONG)
        results = self.eu_sign.cades_verify_data(request_id, new_signature)
        print(results)
        # new_signature = self.eu_sign.cades_make_container(signature, request_id, self.eu_sign.SIGN_TYPE_CADES_X_LONG)
        # results = self.eu_sign.cades_verify_data_internal(new_signature)
        # self.eu_sign.print_verify_results(data_file_path, sign_file_path, results)

    def get_hash(self, request_id: str) -> str:
        try:
            return self.eu_sign.hash_data(request_id)
        except Exception as e:
            print ("Hash data failed. " + str(e))
            
    

