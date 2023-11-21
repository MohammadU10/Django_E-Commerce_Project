from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Spec(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Item(models.Model):
    image = models.ImageField(default='default.png', upload_to='product_pics')
    title = models.CharField(max_length=60)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    content = models.TextField()
    price = models.FloatField()
    discount = models.IntegerField()
    score = models.FloatField()
    
    def discounted_price(self):
        return self.price - (self.price * (self.discount / 100))
    
    def __str__(self):
        return self.title

class ItemSpecs(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    
    def __str__(self):
        return self.value
