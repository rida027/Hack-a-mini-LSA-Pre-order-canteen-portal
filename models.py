from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.name

class ShopOwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    shop_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} - {self.shop_name}"

class Food(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='food_images/', null=True, blank=True)
    shop_owner = models.ForeignKey(ShopOwnerProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.available = False
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('ready', 'Ready'),
        ('collected', 'Collected'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    shop_owner = models.ForeignKey(ShopOwnerProfile, on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    item_status = models.CharField(max_length=20, default='pending')
    
    def get_total_price(self):
        return self.quantity * self.food.price
    
    def __str__(self):
        return f"{self.food.name} x {self.quantity}"
