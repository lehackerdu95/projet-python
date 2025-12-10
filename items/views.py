"""
Views for the items application.
Handles displaying and managing collections and items.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import Collection, Item, Purchase, Auction, Bid, Cart, Offer
from .forms import CollectionForm, ItemForm


class CollectionListView(LoginRequiredMixin, ListView):
    """Display list of collections for the current user."""
    model = Collection
    template_name = 'items/collection_list.html'
    context_object_name = 'collections'
    paginate_by = 10
    
    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)


class CollectionDetailView(LoginRequiredMixin, DetailView):
    """Display details of a specific collection and its items."""
    model = Collection
    template_name = 'items/collection_detail.html'
    context_object_name = 'collection'
    
    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)


class CollectionCreateView(LoginRequiredMixin, CreateView):
    """Create a new collection."""
    model = Collection
    form_class = CollectionForm
    template_name = 'items/collection_form.html'
    success_url = reverse_lazy('collection_list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CollectionUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing collection."""
    model = Collection
    form_class = CollectionForm
    template_name = 'items/collection_form.html'
    
    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('collection_detail', kwargs={'pk': self.object.pk})


class CollectionDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a collection."""
    model = Collection
    template_name = 'items/collection_confirm_delete.html'
    success_url = reverse_lazy('collection_list')
    
    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)


class ItemCreateView(LoginRequiredMixin, CreateView):
    """Create a new item in a collection."""
    model = Item
    form_class = ItemForm
    template_name = 'items/item_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.collection = get_object_or_404(
            Collection,
            pk=kwargs['collection_pk'],
            owner=request.user
        )
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.collection = self.collection
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('collection_detail', kwargs={'pk': self.collection.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collection'] = self.collection
        return context


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing item."""
    model = Item
    form_class = ItemForm
    template_name = 'items/item_form.html'
    
    def get_queryset(self):
        return Item.objects.filter(collection__owner=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('collection_detail', kwargs={'pk': self.object.collection.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collection'] = self.object.collection
        return context


class ItemDeleteView(LoginRequiredMixin, DeleteView):
    """Delete an item from a collection."""
    model = Item
    template_name = 'items/item_confirm_delete.html'
    
    def get_queryset(self):
        return Item.objects.filter(collection__owner=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('collection_detail', kwargs={'pk': self.object.collection.pk})


@login_required
def home(request):
    """Display dashboard for the user."""
    collections = Collection.objects.filter(owner=request.user)
    context = {
        'total_collections': collections.count(),
        'recent_collections': collections[:5],
        'total_items': sum(c.get_item_count() for c in collections),
        'total_value': sum(c.get_total_value() for c in collections),
    }
    return render(request, 'items/home.html', context)


# E-commerce Views

@login_required
def marketplace(request):
    """Display all items for sale from all users."""
    items_for_sale = Item.objects.filter(is_for_sale=True).order_by('-updated_at')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        items_for_sale = items_for_sale.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(collection__name__icontains=search_query)
        )
    
    # Filter by condition
    condition_filter = request.GET.get('condition', '')
    if condition_filter:
        items_for_sale = items_for_sale.filter(condition=condition_filter)
    
    # Sort options
    sort_by = request.GET.get('sort', '-updated_at')
    items_for_sale = items_for_sale.order_by(sort_by)
    
    # Add offer count to each item
    for item in items_for_sale:
        item.offer_count = item.offers.filter(status__in=['pending', 'accepted']).count()
    
    context = {
        'items': items_for_sale,
        'search_query': search_query,
        'condition_filter': condition_filter,
        'sort_by': sort_by,
        'conditions': ['excellent', 'good', 'fair', 'poor'],
    }
    return render(request, 'items/marketplace.html', context)


@login_required
def item_detail(request, pk):
    """Display detailed view of an item with purchase and offer options."""
    item = get_object_or_404(Item, pk=pk, is_for_sale=True)
    offers = item.offers.all().order_by('-created_at')
    user_offer = None
    
    # Get user's offer if exists
    if request.user != item.collection.owner:
        user_offer = item.offers.filter(buyer=request.user, status='pending').first()
    
    # Handle direct purchase
    if request.method == 'POST' and 'buy_now' in request.POST:
        if request.user == item.collection.owner:
            messages.error(request, 'You cannot buy your own item.')
        else:
            # Create a purchase directly at asking price
            purchase = Purchase.objects.create(
                item=item,
                buyer=request.user,
                price_paid=item.sale_price,
                status='completed'
            )
            
            # Mark item as not for sale
            item.is_for_sale = False
            item.save()
            
            # Reject all pending offers
            item.offers.filter(status='pending').update(status='withdrawn')
            
            messages.success(request, f'Purchase successful! You bought {item.name} for ${item.sale_price}')
            return redirect('purchase_history')
    
    # Handle offer submission
    if request.method == 'POST' and 'submit_offer' in request.POST:
        if request.user == item.collection.owner:
            messages.error(request, 'You cannot make an offer on your own item.')
        else:
            amount = request.POST.get('offer_amount')
            message = request.POST.get('offer_message', '')
            
            try:
                amount = float(amount)
                if amount <= 0:
                    messages.error(request, 'Offer amount must be greater than 0.')
                else:
                    # Check if user already has pending offer
                    existing_offer = item.offers.filter(buyer=request.user, status='pending').first()
                    if existing_offer:
                        # Update existing offer
                        existing_offer.amount = amount
                        existing_offer.message = message
                        existing_offer.save()
                        messages.success(request, 'Your offer has been updated!')
                    else:
                        # Create new offer
                        Offer.objects.create(
                            item=item,
                            buyer=request.user,
                            amount=amount,
                            message=message
                        )
                        messages.success(request, 'Your offer has been submitted!')
                    return redirect('item_detail', pk=pk)
            except ValueError:
                messages.error(request, 'Please enter a valid amount.')
    
    context = {
        'item': item,
        'offers': offers,
        'user_offer': user_offer,
        'owner': item.collection.owner,
        'is_owner': request.user == item.collection.owner,
    }
    return render(request, 'items/item_detail.html', context)


@login_required
def upload_item_image(request, pk):
    """Upload or update image for an item."""
    item = get_object_or_404(Item, pk=pk, collection__owner=request.user)
    
    if request.method == 'POST' and request.FILES.get('image'):
        item.image = request.FILES['image']
        item.save()
        messages.success(request, 'Image uploaded successfully!')
        return redirect('item_detail', pk=pk)
    
    context = {'item': item}
    return render(request, 'items/upload_image.html', context)


@login_required
def accept_offer(request, offer_id):
    """Owner accepts an offer."""
    offer = get_object_or_404(Offer, id=offer_id)
    
    # Check if current user is the item owner
    if request.user != offer.item.collection.owner:
        messages.error(request, 'You do not have permission to accept this offer.')
        return redirect('home')
    
    # Reject all other pending offers
    offer.item.offers.filter(status='pending').exclude(id=offer_id).update(status='rejected')
    
    # Accept this offer
    offer.status = 'accepted'
    offer.save()
    
    # Create a purchase record
    Purchase.objects.create(
        item=offer.item,
        buyer=offer.buyer,
        price_paid=offer.amount,
        status='completed'
    )
    
    # Mark item as not for sale
    offer.item.is_for_sale = False
    offer.item.save()
    
    messages.success(request, f'Offer from {offer.buyer.username} accepted!')
    return redirect('item_detail', pk=offer.item.pk)


@login_required
def reject_offer(request, offer_id):
    """Owner rejects an offer."""
    offer = get_object_or_404(Offer, id=offer_id)
    
    # Check if current user is the item owner
    if request.user != offer.item.collection.owner:
        messages.error(request, 'You do not have permission to reject this offer.')
        return redirect('home')
    
    offer.status = 'rejected'
    offer.save()
    
    messages.info(request, f'Offer from {offer.buyer.username} rejected.')
    return redirect('item_detail', pk=offer.item.pk)


@login_required
def add_to_cart(request, pk):
    """Add an item to the user's shopping cart."""
    item = get_object_or_404(Item, pk=pk, is_for_sale=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.add(item)
    return redirect('view_cart')


@login_required
def view_cart(request):
    """Display the user's shopping cart."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {
        'cart': cart,
        'total_price': cart.get_total_price(),
        'item_count': cart.get_item_count(),
    }
    return render(request, 'items/cart.html', context)


@login_required
def remove_from_cart(request, pk):
    """Remove an item from the user's shopping cart."""
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(Item, pk=pk)
    cart.items.remove(item)
    return redirect('view_cart')


@login_required
def checkout(request):
    """Process purchase of items in cart."""
    cart = get_object_or_404(Cart, user=request.user)
    
    if request.method == 'POST':
        # Create purchase records for each item
        for item in cart.items.all():
            if item.is_for_sale and item.sale_price:
                Purchase.objects.create(
                    item=item,
                    buyer=request.user,
                    price_paid=item.sale_price,
                    status='completed'
                )
        # Clear the cart
        cart.items.clear()
        return redirect('purchase_success')
    
    context = {
        'cart': cart,
        'total_price': cart.get_total_price(),
    }
    return render(request, 'items/checkout.html', context)


@login_required
def purchase_success(request):
    """Display purchase success message."""
    purchases = Purchase.objects.filter(buyer=request.user).order_by('-purchase_date')[:5]
    context = {
        'purchases': purchases,
    }
    return render(request, 'items/purchase_success.html', context)


@login_required
def purchase_history(request):
    """Display user's purchase history."""
    purchases = Purchase.objects.filter(buyer=request.user).order_by('-purchase_date')
    context = {
        'purchases': purchases,
    }
    return render(request, 'items/purchase_history.html', context)


# Auction Views

@login_required
def create_auction(request, pk):
    """Create an auction for an item."""
    item = get_object_or_404(Item, pk=pk, collection__owner=request.user)
    
    if request.method == 'POST':
        from django.utils import timezone
        from datetime import timedelta
        
        starting_price = request.POST.get('starting_price')
        duration_days = request.POST.get('duration_days', 7)
        
        auction = Auction.objects.create(
            item=item,
            seller=request.user,
            starting_price=starting_price,
            current_price=starting_price,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=int(duration_days)),
            status='active'
        )
        return redirect('auction_detail', pk=auction.pk)
    
    context = {
        'item': item,
    }
    return render(request, 'items/create_auction.html', context)


@login_required
def auction_list(request):
    """Display list of active auctions."""
    auctions = Auction.objects.filter(status='active').order_by('-start_date')
    context = {
        'auctions': auctions,
    }
    return render(request, 'items/auction_list.html', context)


@login_required
def auction_detail(request, pk):
    """Display details of a specific auction."""
    auction = get_object_or_404(Auction, pk=pk)
    
    if request.method == 'POST' and auction.is_active():
        bid_amount = request.POST.get('bid_amount')
        
        if float(bid_amount) > auction.current_price:
            Bid.objects.create(
                auction=auction,
                bidder=request.user,
                amount=bid_amount
            )
            auction.current_price = bid_amount
            auction.highest_bidder = request.user
            auction.save()
            return redirect('auction_detail', pk=auction.pk)
    
    bids = auction.bids.all().order_by('-bid_date')
    context = {
        'auction': auction,
        'bids': bids,
        'is_seller': auction.seller == request.user,
        'can_bid': auction.is_active() and auction.seller != request.user,
    }
    return render(request, 'items/auction_detail.html', context)


@login_required
def my_auctions(request):
    """Display user's auctions."""
    auctions = Auction.objects.filter(seller=request.user).order_by('-start_date')
    context = {
        'auctions': auctions,
    }
    return render(request, 'items/my_auctions.html', context)


@login_required
def end_auction(request, pk):
    """End an auction and mark as sold if there's a highest bidder."""
    auction = get_object_or_404(Auction, pk=pk, seller=request.user)
    
    if auction.highest_bidder:
        auction.status = 'sold'
        # Create purchase record for winning bidder
        Purchase.objects.create(
            item=auction.item,
            buyer=auction.highest_bidder,
            price_paid=auction.current_price,
            status='completed'
        )
    else:
        auction.status = 'ended'
    
    auction.save()
    return redirect('my_auctions')
