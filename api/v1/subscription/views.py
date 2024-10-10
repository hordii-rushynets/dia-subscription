from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class SuccessView(APIView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        return Response({"success": True}, status=status.HTTP_200_OK)
