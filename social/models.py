from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser,BaseUserManager
# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self,username,password,email):
        if not email:
            raise ValueError('provide a valid email')
        if not username:
            raise ValueError('provide username')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,username,password,email):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name='User Email',max_length=100,unique=True,null=False)
    username = models.CharField(verbose_name='Username',unique=True,null=False,max_length=50)
    first_name = models.CharField(verbose_name='first_name',unique=False,null=True,blank=True, max_length=100)
    last_name = models.CharField(verbose_name='last_name',unique=False,null=True,blank=True,max_length=100)
    followers = models.ManyToManyField('self',symmetrical=False, blank=True,related_name='following', default=0)
    @property
    def followerscount(self):
        follower_count = self.following.all().count()
        return str(follower_count)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    
    def __str__(self):
        return self.username
# Model for user posts
class Post(models.Model):
    content = models.TextField()  # The text content of the post
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # The user who created the post
    timestamp = models.DateTimeField(auto_now_add=True)  # Time the post was created
    media = models.URLField(blank=True, null=True)  # Optional field for media (image/video) URLs
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, blank=True, null=True)  # Type of media (optional)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"  # Returns a string representation of the post


# Model for managing following relationships between users

# Model for user profiles
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # One-to-one relationship with User
    bio = models.TextField(blank=True, null=True)  # Optional bio field
    profile_picture = models.URLField(blank=True, null=True)  # Optional field for the profile picture URL

    def __str__(self):
        return f"{self.user.username}'s Profile"  # Returns a string representation of the profile


# Signal to automatically create or update a user's profile when the user is created or updated
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)  # Create profile when a new user is created
    instance.profile.save()  # Save the profile every time the user is saved
