from django.urls import path
from .views import ParsedResumeView, GetResume

urlpatterns = [
    path('parse/', ParsedResumeView.as_view()),
    path("getresume/", GetResume.as_view(), name="get-resume"),
]