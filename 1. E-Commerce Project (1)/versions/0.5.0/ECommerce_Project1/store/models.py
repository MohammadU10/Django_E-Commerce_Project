from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    title = models.charfield(max_length=50)
    content = models.TextField()
    price = models.FloatField()
    discount = models.IntegerField()
    score = models.FloatField()
    
    def __str__(self):
        return self.title
