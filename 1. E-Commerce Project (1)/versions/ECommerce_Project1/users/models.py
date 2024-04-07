from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image


class CustomUser(AbstractUser):
    """
    Custom user model with custom attributes, for managing Auth system and user data.
    """
    first_name = models.TextField(max_length=50)
    last_name = models.TextField(max_length=50)
    phone_number = PhoneNumberField(blank=True, null=True, unique=True, max_length=12)
    address = models.TextField(max_length=200)
    
    def __str__(self):
        """
        Returns a string representation of the CustomUser object.
        """
        return f'{self.username} Personal Info'


class Profile(models.Model):
    """
    Model representing a Profile for each user, for managing user profile images.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(default='default_profile.jpg', upload_to='profile_pics')

    def __str__(self):
        """
        Returns a string representation of the Profile object.
        """
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to resize the profile picture if it exceeds 300x300 pixels.
        """
        super().save(*args, **kwargs)
        
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
