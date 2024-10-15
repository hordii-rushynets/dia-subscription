from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import base64
import json
from apps.dia_subscription_users import services


class SuccessView(APIView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        encoded_data = request.data.get('encodeData')
        print(f'Encoded data: {encoded_data} \n')
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')

        data = json.loads(decoded_data)
        print("Data:", data, "\n\n")
        # data = request.data

        signature = data.get('signature')
        request_id = data.get('requestId')
        service = services.DIASubscriptionService()
        
        result = service.get_user_data(signature, request_id)
        print("Result:", result, "\n")

        hash = service.get_hash(request_id)
        print("Hash:", hash, "\n")

        return Response({"success": True}, status=status.HTTP_200_OK)
