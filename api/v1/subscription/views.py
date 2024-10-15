from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
import base64
import json

from apps.dia_subscription_users import services, models
from api.v1.subscription import serializers


class CompanyView(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        queryset = models.Company.objects.all()
        return Response(serializers.CompanySerializer(queryset, many=True).data)


class DeeplinkView(APIView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        company_id = request.data.get('id')
        if not models.Company.objects.filter(id=company_id).exists():
            raise ValidationError(f'Company with ID: {company_id} does not exists.')

        service = services.DIASubscriptionService()
        acquirer_token = service.get_acquirer_token()
        branch_id = service.create_branch(acquirer_token)
        branch_offer_id = service.create_branch_offer(acquirer_token, branch_id)
        deeplink = service.make_offer_request(acquirer_token, branch_id, branch_offer_id, company_id)
        return Response({"deeplink": deeplink}, status=status.HTTP_200_OK)


class SuccessView(APIView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        encoded_data = request.data.get('encodeData')
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')

        data = json.loads(decoded_data)

        signature = data.get('signature')
        request_id = data.get('requestId')
        service = services.DIASubscriptionService()

        result = service.get_user_data(signature, request_id)

        serializer = serializers.SignerSerializer(data=result)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"success": True}, status=status.HTTP_200_OK)


class ValidateSign(APIView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        data = request.data
        signature = data.get('signature')
        request_id = data.get('requestId')
        service = services.DIASubscriptionService()
        
        result = service.get_user_data(signature, request_id)

        serializer = serializers.SignerSerializer(data=result)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"success": True}, status=status.HTTP_200_OK)