from django.contrib.auth import password_validation
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'age',
            'can_be_contacted',
            'can_data_be_shared',
            'created_time',
        ]
        read_only_fields = ['id', 'created_time']

    def validate_password(self, password):
        user = User(
            username=self.initial_data.get(
                'username',
                getattr(self.instance, 'username', ''),
            ),
            first_name=self.initial_data.get(
                'first_name',
                getattr(self.instance, 'first_name', ''),
            ),
            last_name=self.initial_data.get(
                'last_name',
                getattr(self.instance, 'last_name', ''),
            ),
            email=self.initial_data.get(
                'email',
                getattr(self.instance, 'email', ''),
            ),
        )
        password_validation.validate_password(password, user=user)
        return password

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(
            password=password,
            **validated_data,
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
