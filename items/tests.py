"""
Tests for items app models.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from items.models import Collection, Item


class CollectionModelTest(TestCase):
    """Test cases for Collection model."""
    
    def setUp(self):
        """Create test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.collection = Collection.objects.create(
            owner=self.user,
            name='Test Collection',
            description='A test collection'
        )
    
    def test_collection_creation(self):
        """Test creating a collection."""
        self.assertEqual(self.collection.name, 'Test Collection')
        self.assertEqual(self.collection.owner, self.user)
    
    def test_get_total_value(self):
        """Test total value calculation."""
        Item.objects.create(
            collection=self.collection,
            name='Item 1',
            value=100.00
        )
        Item.objects.create(
            collection=self.collection,
            name='Item 2',
            value=50.00
        )
        self.assertEqual(self.collection.get_total_value(), 150.00)
    
    def test_get_item_count(self):
        """Test item count."""
        Item.objects.create(
            collection=self.collection,
            name='Item 1',
            value=100.00
        )
        self.assertEqual(self.collection.get_item_count(), 1)
    
    def test_collection_str(self):
        """Test string representation."""
        self.assertEqual(str(self.collection), 'Test Collection')


class ItemModelTest(TestCase):
    """Test cases for Item model."""
    
    def setUp(self):
        """Create test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.collection = Collection.objects.create(
            owner=self.user,
            name='Test Collection'
        )
        self.item = Item.objects.create(
            collection=self.collection,
            name='Test Item',
            value=99.99
        )
    
    def test_item_creation(self):
        """Test creating an item."""
        self.assertEqual(self.item.name, 'Test Item')
        self.assertEqual(self.item.value, 99.99)
        self.assertEqual(self.item.condition, 'good')
    
    def test_item_str(self):
        """Test string representation."""
        self.assertEqual(str(self.item), 'Test Item')
