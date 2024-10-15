from django.urls import path
from .views import SuccessView, DeeplinkView


urlpatterns = [
    path('success', SuccessView.as_view(), name='success'),
    path('deeplink', DeeplinkView.as_view(), name='deeplink'),
]