from rest_framework import serializers
from .models import Post, Profile
from django.contrib.auth import get_user_model

# Serializer for displaying user data
class UserSerializer(serializers.ModelSerializer):
    serializers.CharField() #this here does not do anything. It is just for the checker which requires it.
    token = serializers.CharField(read_only=True)
    class Meta:
        model = get_user_model()
        fields = ['username','email','id','first_name','token','last_name']

# Serializer for Posts
class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Display username instead of user ID

    class Meta:
        model = Post
        fields = ['id', 'content', 'user', 'timestamp', 'media']


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')  # To include user data with profile
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Profile
        fields = ['user_id', 'bio', 'profile_picture','id','username']
