"""URL configuration for items app."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('collections/', views.CollectionListView.as_view(), name='collection_list'),
    path('collections/create/', views.CollectionCreateView.as_view(), name='collection_create'),
    path('collections/<int:pk>/', views.CollectionDetailView.as_view(), name='collection_detail'),
    path('collections/<int:pk>/update/', views.CollectionUpdateView.as_view(), name='collection_update'),
    path('collections/<int:pk>/delete/', views.CollectionDeleteView.as_view(), name='collection_delete'),
    path('collections/<int:collection_pk>/items/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/update/', views.ItemUpdateView.as_view(), name='item_update'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    
    # E-commerce URLs - Shopping Cart & Purchases
    path('marketplace/', views.marketplace, name='marketplace'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/<int:pk>/upload-image/', views.upload_item_image, name='upload_item_image'),
    path('offers/<int:offer_id>/accept/', views.accept_offer, name='accept_offer'),
    path('offers/<int:offer_id>/reject/', views.reject_offer, name='reject_offer'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('purchase-success/', views.purchase_success, name='purchase_success'),
    path('purchases/', views.purchase_history, name='purchase_history'),
    
    # Auction URLs
    path('auctions/', views.auction_list, name='auction_list'),
    path('auctions/<int:pk>/', views.auction_detail, name='auction_detail'),
    path('items/<int:pk>/auction/create/', views.create_auction, name='create_auction'),
    path('my-auctions/', views.my_auctions, name='my_auctions'),
    path('auctions/<int:pk>/end/', views.end_auction, name='end_auction'),
]
