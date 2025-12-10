"""
Admin configuration for items app.
"""

from django.contrib import admin
from .models import Collection, Item, Purchase, Auction, Bid, Cart, Offer


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Admin interface for Collection model."""
    list_display = ('name', 'owner', 'created_at', 'get_item_count', 'get_total_value')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_item_count(self, obj):
        return obj.get_item_count()
    get_item_count.short_description = 'Items Count'
    
    def get_total_value(self, obj):
        return f"€{obj.get_total_value()}"
    get_total_value.short_description = 'Total Value'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin interface for Item model."""
    list_display = ('name', 'collection', 'value', 'condition', 'is_for_sale', 'sale_price', 'created_at')
    list_filter = ('condition', 'created_at', 'collection', 'is_for_sale')
    search_fields = ('name', 'description', 'collection__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Admin interface for Purchase model."""
    list_display = ('buyer', 'item', 'price_paid', 'status', 'purchase_date')
    list_filter = ('status', 'purchase_date')
    search_fields = ('buyer__username', 'item__name')
    readonly_fields = ('purchase_date',)


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    """Admin interface for Auction model."""
    list_display = ('item', 'seller', 'starting_price', 'current_price', 'highest_bidder', 'status', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('item__name', 'seller__username')
    readonly_fields = ('start_date',)


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    """Admin interface for Bid model."""
    list_display = ('bidder', 'auction', 'amount', 'bid_date')
    list_filter = ('bid_date', 'auction')
    search_fields = ('bidder__username', 'auction__item__name')
    readonly_fields = ('bid_date',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin interface for Cart model."""
    list_display = ('user', 'get_item_count', 'get_total_price', 'created_at')
    filter_horizontal = ('items',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_item_count(self, obj):
        return obj.get_item_count()
    get_item_count.short_description = 'Items in Cart'
    
    def get_total_price(self, obj):
        return f"€{obj.get_total_price()}"
    get_total_price.short_description = 'Total Price'


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin interface for Offer model."""
    list_display = ('buyer', 'item', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'item')
    search_fields = ('buyer__username', 'item__name', 'message')
    readonly_fields = ('created_at', 'updated_at')
