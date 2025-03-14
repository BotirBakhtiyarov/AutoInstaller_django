from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default_profile.jpg')
    real_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}'s Profile"

