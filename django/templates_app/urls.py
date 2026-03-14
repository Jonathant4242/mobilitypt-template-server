from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("request/", views.request_view, name="request"),
]
