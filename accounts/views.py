from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import SignUpSerializer


class SignUpAPIView(CreateAPIView):
    serializer_class = SignUpSerializer


class LogOutAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        token = get_object_or_404(Token, user=self.request.user)

        token.delete()

        return JsonResponse({'status': 'Success'})
