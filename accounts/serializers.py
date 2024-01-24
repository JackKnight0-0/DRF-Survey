from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True,
                                   validators=[UniqueValidator(get_user_model().objects.all())])
    password1 = serializers.CharField(required=True, write_only=True,
                                      validators=[validate_password])
    password2 = serializers.CharField(required=True, write_only=True,
                                      validators=[validate_password])

    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'email',
            'password1',
            'password2'
        )

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise ValidationError({'password2': 'The password not matching!'})
        return attrs

    def create(self, validated_data):
        vd = validated_data
        user = get_user_model().objects.create_user(username=vd.get('username'), email=vd.get('email'))

        user.set_password(vd.get('password1'))

        user.save()

        return user
