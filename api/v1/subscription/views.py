from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import base64
import json


class SuccessView(APIView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        print("Encoded request data:", request.data , "\n\n")
        encoded_data = request.data.get('encodeData')

        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        print("Decoded request data:", decoded_data, "\n\n")

        data = json.loads(decoded_data)
        print("Data:", data, "\n\n")
        return Response({"success": True}, status=status.HTTP_200_OK)
