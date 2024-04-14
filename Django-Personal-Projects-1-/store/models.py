from django.db import models
from django.urls import reverse

class Category(models.Model):
    """
    Model representing a category for items.
    """
    name = models.CharField(max_length=255) # Field for the category name

    def __str__(self):
        """
        Return the name of the category.
        """
        return f'{self.name}'


class Brand(models.Model):
    """
    Model representing a brand/manufacturer for items.
    """
    name = models.CharField(max_length=255) # Field for the brand name

    def __str__(self):
        """
        Return the name of the brand.
        """
        return f'{self.name}'


class Spec(models.Model):
    """
    Model representing a type of items spec(eg. color, storage, ports,...) with their name and corresponding Category.
    """
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
  
    def __str__(self):
        return f'{self.name}'


class Item(models.Model):
    """
    Model representing an item (product) with its various attributes.
    """
    image = models.ImageField(default='default_product.png', upload_to='product_pics') # Image field for the item
    title = models.CharField(max_length=60) # Field for the item title/name
    content = models.TextField() # Field for the item description, content, & specs
    specs = models.ManyToManyField(Spec, through='ItemSpecValue')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, blank=True, on_delete=models.CASCADE)
    stock_quantity = models.IntegerField(default=0) # Field for the item stock quantity
    discount = models.IntegerField(default=0, help_text='Enter the discount percentage as an integer.') # Discount Percentage
    price = models.FloatField() # Field for the item price, 8 max digits & up to 2 decimal places
    score = models.FloatField(default=0.0) # Field for the item review score

    def discounted_price(self):
        """
        Calculate the price of the item after applying the discount.
        """
        if self.discount:
            return self.price * (1 - self.discount / 100)
        else:
            return self.price

    def __str__(self):
        """
        Return the title of the item.
        """
        return f'{self.title}'

    def get_absolute_url(self):
        """
        Return the URL for viewing this item.
        """
        return reverse('item-detail', kwargs={"pk": self.pk})

    class Meta:
        ordering = ['-pk']


class ItemSpecValue(models.Model):
    """
    Many-To-Many Relationship Model for the Item and Spec models, with the actual value.
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
  
    def __str__(self):
        """
        Returns a string representation of the ItemSpecValue object,
        which is a combination of the item name, spec name, and value.
        """
        return f'{self.value}'
