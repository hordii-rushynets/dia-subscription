from django.urls import path
from .views import SuccessView, DeeplinkView, ValidateSignStatusView, CompanyView


urlpatterns = [
    path('success', SuccessView.as_view(), name='success'),
    path('deeplink', DeeplinkView.as_view(), name='deeplink'),
    path('validate-sign', ValidateSignStatusView.as_view(), name='validate-sign'),
    path('company', CompanyView.as_view(), name='company'),
]