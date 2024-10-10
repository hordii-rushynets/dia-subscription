from django.urls import path
from .views import SuccessView


urlpatterns = [
    path('success/', SuccessView.as_view(), name='success'),
]