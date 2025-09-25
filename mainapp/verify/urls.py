from django.urls import path
from . import views

app_name = "verify"
urlpatterns = [
    path("send/", views.send_verification, name="send"),
    path("go/<uuid:token>/", views.verify, name="verify"),
]
