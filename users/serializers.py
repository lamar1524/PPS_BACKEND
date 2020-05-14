from .models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'image']
        extra_kwargs = {'password': {'write_only': True}}

    def to_representation(self, instance):
        to_return = super().to_representation(instance)
        if to_return['image']:
            to_return['image'] = 'http://' + self.context['host'] + to_return['image']
        return to_return

    def create(self, validates_data):
        return User.objects.create_user(**validates_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.image = validated_data.get('image', instance.image)
        if validated_data.get('password'):
            instance.set_password(raw_password=validated_data.get('password'))
        instance.save()
        return instance
