from django.urls import path
from .views import SuccessView, DeeplinkView, ValidateSign, CompanyView


urlpatterns = [
    path('success', SuccessView.as_view(), name='success'),
    path('deeplink', DeeplinkView.as_view(), name='deeplink'),
    path('validate-sign', ValidateSign.as_view(), name='validate-sign'),
    path('company', CompanyView.as_view(), name='company'),
]