from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    image = models.ImageField(default='default.png', upload_to='product_pics')
    title = models.CharField(max_length=50)
    content = models.TextField()
    price = models.FloatField()
    discount = models.IntegerField()
    score = models.FloatField()
    
    def discounted_price(self):
        return self.price - (self.price * (self.discount / 100))
    
    def __str__(self):
        return self.title
