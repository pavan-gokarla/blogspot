from rest_framework import serializers


from app.models import Blog, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
