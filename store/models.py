from django.db import models
from django.urls import reverse
from django.utils import timezone
from users.models import CustomUser
from decimal import Decimal
import uuid


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
    def get_absolute_url(self):
        """
        Return the URL for viewing this Category Items page.
        """
        return reverse('categories', kwargs={"name": self.name})

    class Meta:
        ordering = ['-pk']


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
        return f'{self.category_id} - {self.name}'


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
    stock_quantity = models.PositiveIntegerField(default=0) # Field for the item stock quantity
    discount = models.PositiveIntegerField(default=0, help_text='Enter the discount percentage as an integer.') # Discount Percentage
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
        return f'{self.item} - {self.spec} - {self.value}'


class Cart(models.Model):
    """
    Model for managing User Cart which contains the items added by the User.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)
    items = models.ManyToManyField(Item, through='CartItem')

    def __str__(self):
        """
        Returns a string representation of the Cart object,
        """
        return f'{self.user}\'s Cart'


class CartItem(models.Model):
    """
    Model for managing Cart items and their quantity.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        """
        Returns a string representation of the CartItem objects,
        """
        return f'{self.cart.user}\'s {self.item.title} ({self.quantity})'


class Review(models.Model):
    """
    Model for managing Item Reviews added by the User.
    """
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        """
        Returns a string representation of the Review object,
        """
        return f'{self.item} Review by {self.author}'


class Order(models.Model):
    """
    Model for managing User Orders after checkout.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    items = models.ManyToManyField(Item, through='OrderItem', related_name='orders')
    created_at = models.DateTimeField(default=timezone.now)
    shipping_date = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=4, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.CharField()
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        """
        Returns a string representation of the Order object,
        """
        return f'{self.user.username}\'s Order #{self.id}'


class OrderItem(models.Model):
    """
    Model for managing Order items and their submitted quantity and price.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    
    def __str__(self):
        """
        Returns a string representation of the OrderItem objects,
        """
        return f'Order #{self.order.id} {self.item.title} ({self.quantity})'
