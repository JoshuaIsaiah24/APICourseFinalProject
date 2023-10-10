from rest_framework import serializers
from .models import MenuItem, Category, Order, OrderItem, Cart
from django.contrib.auth.models import User, Group

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug', 'title']
        
class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.title', read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='menuitem.price', read_only=True)
    title = serializers.CharField(source='menuitem.title', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class OrderSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    date = serializers.DateTimeField(format="%m/%d/%Y", input_formats=["%m/%d/%Y"])
    user = serializers.CharField(source= 'user.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date']
        
    def get_is_out_for_delivery(self, obj):
        # Check if delivery_crew is assigned and status is 0
        return obj.delivery_crew is not None and obj.status == 0
    
    data = {
    'my_datetime_field': '10/06/2023',
    }
    
    
    

class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source = 'menuitem.price', read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source = 'cart.price', read_only=True)
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
        

class CartSerializer(serializers.ModelSerializer):
   item = serializers.CharField(source = 'menuitem.title', read_only=True)
   unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source = 'menuitem.price', read_only=True)
   
   class Meta:
        model = Cart
        fields = ['id', 'item', 'menuitem', 'quantity', 'unit_price', 'price']
        
        extra_kwargs = {
        'price': {'read_only': True},   
        }
        
        
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
