from django.urls import path

from .views import ViewClicksInfo

urlpatterns = [
    path('clicks_info/<str:api_flags>', ViewClicksInfo.as_view()),
    path('clicks_info', ViewClicksInfo.as_view()),
]