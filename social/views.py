from django.shortcuts import get_object_or_404
from .models import CustomUser
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes,authentication_classes
from rest_framework.authentication import TokenAuthentication,BasicAuthentication,SessionAuthentication
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from .models import Post, Profile
from rest_framework.generics import RetrieveUpdateAPIView
from .serializers import PostSerializer, ProfileSerializer,UserSerializer

User = get_user_model()
# Create your views here.
class CrudPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user
       
#signup view
@api_view(['POST'])
def signup(request):
    """
    user gets to register
    required json details include
    {
            "username":"sample",
            "email":"sample@gmail.com",
            "password":"samplepassword",
            }
    it is a post method."""
    serializer = UserSerializer(data=request.data)
    #check validity of serializer
    if serializer.is_valid():
        serializer.save()
        #get the user
        user = CustomUser.objects.get(email=request.data['email'])
        #use django set password to hash the password from user
        user.set_password(request.data['password'])
        user.save()
        #get the token by creating it and assigning user to current user
        token,created = Token.objects.get_or_create(user=user)
        #here we return response containing json details, such as token key and serializer data
        return Response({"token":token.key,"user":serializer.data})
#login view
@api_view(['POST'])
#allow user login
def login(request):
    """
    user gets to register
    required json details include
    {
            "email":"sample@gmail.com",
            "password":"samplepassword",
            }
    it is a post method."""
    user = get_object_or_404(CustomUser,email=request.data['email'])
    #first we check whether user has entered the right password
    if not user.check_password(request.data['password']):
        return Response({"details":"not found"},status=status.HTTP_400_BAD_REQUEST)
    token, created = Token.objects.get_or_create(user=user)
    #we return user details
    serializer = UserSerializer(instance=user)
    return Response({"token":token.key,"user":serializer.data})
# Custom pagination for posts
class FeedPagination(PageNumberPagination):
    page_size = 10  # You can set a custom page size here
    page_size_query_param = 'page_size'
    max_page_size = 100  # Optional limit on the maximum page size
@authentication_classes([TokenAuthentication,BasicAuthentication,SessionAuthentication])    
class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated,CrudPermissions]
    pagination_class = FeedPagination
    def perform_create(self, serializer):
        # Save the post with the current user as the author
        serializer.save(user=self.request.user)
#follow
@permission_classes(IsAuthenticated)
@api_view(['POST'])
@authentication_classes([TokenAuthentication,BasicAuthentication,SessionAuthentication])
def follow(request, pk):    
    user_to_be_followed = get_object_or_404(CustomUser,id=pk)
    user_doing_the_following = request.user
    if user_to_be_followed:
        if request.user.id == user_to_be_followed.id:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        elif user_doing_the_following.following.filter(id=user_to_be_followed.id).exists():
            return Response({"error": f"You cannot follow {user_to_be_followed} twice."}, status=status.HTTP_400_BAD_REQUEST)
        user_doing_the_following.following.add(user_to_be_followed)
        return Response({"success":f"Followed {user_to_be_followed.username}"})
    return Response(
        {"error": "Method not allowed."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )
@authentication_classes([TokenAuthentication,BasicAuthentication,SessionAuthentication])
@permission_classes(IsAuthenticated)
@api_view(['POST'])
def unfollow(request,pk):
    user_to_be_unfollowed = get_object_or_404(CustomUser,id=pk)
    user_doing_the_following = request.user
    if user_to_be_unfollowed:
        user_doing_the_following.following.remove(user_to_be_unfollowed)
        return Response({"success":f"Unfollowed {user_to_be_unfollowed.username}"})
#unfollow
@authentication_classes([TokenAuthentication,BasicAuthentication,SessionAuthentication])
@permission_classes([IsAuthenticated])
class RetrievedProfileUpdateProfile(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    def get_object(self):
        return Profile.objects.get(user=self.request.user)