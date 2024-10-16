from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import signup, login,PostView,follow,unfollow,RetrievedProfileUpdateProfile



# Set up router for ViewSets
router = DefaultRouter()
router.register(r'postview',PostView,basename='postview')

# URL patterns for the app
urlpatterns = [
    path('', include(router.urls)),  # API endpoints (for posts, followers, profiles)
    path('login/', login, name='login'),  # Redirect logged-in users
    path('api-auth/',include('rest_framework.urls')),
    path('signup/', signup, name='signup'),  # Path for user signup
    path('follow/<int:pk>/',follow,name='follow'),
    path('unfollow/<int:pk>/',unfollow,name='unfollow'),
    path('profile/',RetrievedProfileUpdateProfile.as_view(),name='profile'),
]
