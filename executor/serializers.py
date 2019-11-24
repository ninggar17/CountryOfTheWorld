from django.contrib.auth.models import User, Group
from rest_framework import serializers
from executor.query_executor import CountryInfo


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField()
    res = serializers.DictField(read_only=True)

    def create(self, validated_data):
        return CountryInfo(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance
