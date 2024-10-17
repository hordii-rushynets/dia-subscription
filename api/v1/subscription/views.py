from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
import base64
import json
from django.core.cache import cache

from apps.dia_subscription_users import services, models
from api.v1.subscription import serializers


class CompanyView(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        queryset = models.Company.objects.all()
        return Response(serializers.CompanySerializer(queryset, many=True).data)


class DeeplinkView(APIView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        vote_business_id = request.data.get('vote_business')
        vote_business_veterans_id = request.data.get('vote_business_veterans')

        if not vote_business_id or not vote_business_veterans_id:
            raise ValidationError('vote_business_id  and vote_business_veterans_id is required.')

        service = services.DIASubscriptionService()
        acquirer_token = service.get_acquirer_token()
        branch_id = service.create_branch(acquirer_token)
        branch_offer_id = service.create_branch_offer(acquirer_token, branch_id)
        deeplink = service.make_offer_request(acquirer_token, branch_id, branch_offer_id, vote_business_id, vote_business_veterans_id)
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
        print("result:", result)

        serializer = serializers.SignerSerializer(data=result)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print("Errors:", serializer.errors)

        cache.set(f'{request_id}_status', True, timeout=60*4)
        return Response({"success": True}, status=status.HTTP_200_OK)


class ValidateSignStatusView(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        request_id = request.query_params.get('requestId')
        request_id_status = cache.get(f'{request_id}_status')

        if not request_id_status:
            return Response({"detail": "Redirecting..."}, status=status.HTTP_302_FOUND, headers={'Location': f'{settings.FRONTEND_DOMAIN}/success.html?vote=already=true'})

        return Response({"detail": "Redirecting..."}, status=status.HTTP_302_FOUND, headers={'Location': f'{settings.FRONTEND_DOMAIN}/success.html'})
        

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