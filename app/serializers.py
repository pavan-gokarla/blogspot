from rest_framework import serializers

from .models import Blog, CodeSnippets, Tags


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = "__all__"


class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSnippets
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = "__all__"

