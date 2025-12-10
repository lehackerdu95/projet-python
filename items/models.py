"""
Models for the items application.
Represents objects and collections for economics tracking.
"""

from django.db import models
from django.contrib.auth.models import User


class Collection(models.Model):
    """
    Represents a collection of objects.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Collections'
    
    def __str__(self):
        return self.name
    
    def get_total_value(self):
        """Calculate total value of all objects in collection."""
        return sum(obj.value for obj in self.items.all())
    
    def get_item_count(self):
        """Get count of objects in collection."""
        return self.items.count()


class Item(models.Model):
    """
    Represents an individual object in a collection.
    """
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    acquisition_date = models.DateField(null=True, blank=True)
    condition = models.CharField(
        max_length=50,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        default='good'
    )
    image = models.ImageField(upload_to='items/', null=True, blank=True)
    is_for_sale = models.BooleanField(default=False)  # Can be purchased
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
    
    def __str__(self):
        return self.name


class Purchase(models.Model):
    """
    Represents a purchase of an item.
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='purchases')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    class Meta:
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"{self.buyer.username} bought {self.item.name}"


class Auction(models.Model):
    """
    Represents an auction for an item.
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='auctions')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions_created')
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    highest_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auction_bids')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('active', 'Active'),
            ('ended', 'Ended'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        default='active'
    )
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Auction: {self.item.name} (${self.current_price})"
    
    def is_active(self):
        """Check if auction is still active."""
        from django.utils import timezone
        return self.status == 'active' and self.end_date > timezone.now()


class Bid(models.Model):
    """
    Represents a bid on an auction.
    """
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-bid_date']
    
    def __str__(self):
        return f"{self.bidder.username} bid ${self.amount} on {self.auction.item.name}"


class Cart(models.Model):
    """
    Shopping cart for purchases.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    items = models.ManyToManyField(Item, related_name='in_carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart of {self.user.username}"
    
    def get_total_price(self):
        """Calculate total price of items in cart."""
        return sum(item.sale_price for item in self.items.filter(is_for_sale=True))
    
    def get_item_count(self):
        """Get count of items in cart."""
        return self.items.count()


class Offer(models.Model):
    """
    Represents an offer on an item (for negotiation).
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='offers')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers_made')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('withdrawn', 'Withdrawn'),
        ],
        default='pending'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Offer: {self.buyer.username} offered ${self.amount} for {self.item.name}"
