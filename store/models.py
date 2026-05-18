from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify



def generate_unique_slug(instance, value, slug_field_name='slug'):
    """Generate a unique slug for a model instance."""
    slug_base = slugify(value)
    slug = slug_base
    Model = instance.__class__
    counter = 1
    while Model.objects.filter(**{slug_field_name: slug}).exclude(pk=instance.pk).exists():
        slug = f"{slug_base}-{counter}"
        counter += 1
    return slug


# ====================== Custom User Model ======================
class User(AbstractUser):
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or self.email

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


# ====================== Category ======================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


# ====================== Product ======================
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)          # New field
    rating = models.FloatField(default=0.0)
    stock = models.PositiveIntegerField(default=0)
    
    weight = models.CharField(max_length=50, blank=True)
    origin = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100, 1)
        return 0

    class Meta:
        ordering = ['-featured', 'name']


# ====================== Wishlist ======================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')   # One user can't wishlist same product twice
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ====================== Order ======================
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('netbanking', 'Net Banking'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Shipping Details
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="India")
    
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    notes = models.TextField(blank=True)

    # Order Info
    total = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    upi_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    payment_status = models.CharField(max_length=20, default='pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']


# ====================== OrderItem ======================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def get_total(self):
        return self.price * self.quantity

    class Meta:
        ordering = ['id']
        