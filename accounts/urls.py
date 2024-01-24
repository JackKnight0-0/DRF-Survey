from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import SignUpAPIView, LogOutAPIView

urlpatterns = [
    path('signup/', SignUpAPIView.as_view()),
    path('login/', obtain_auth_token),
    path('logout/', LogOutAPIView.as_view())
]
