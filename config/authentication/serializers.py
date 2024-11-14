from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username'
            ]
        read_only_fields = ['id']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'can_be_contacted',
            'can_data_be_shared',
            'age',
            ]
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'can_be_contacted',
            'can_data_be_shared',
            'age',
            ]
        write_only_fields = ['password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            can_be_contacted=validated_data['can_be_contacted'],
            can_data_be_shared=validated_data['can_data_be_shared'],
            age=validated_data['age'],
            password=validated_data['password']
        )
        return user
