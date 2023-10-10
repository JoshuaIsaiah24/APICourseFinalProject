from django.shortcuts import render
from rest_framework import generics
from .models import MenuItem, Category, OrderItem, Order, Cart
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, OrderItemSerializer, OrderSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.models import User, Group
from .permissions import UserReadOnlyPermission, ManagerPermission
from decimal import Decimal
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# Create your views here.
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    

class MenuItemViews(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    ordering_fields = ['price', 'category']
    filterset_fields = ['price', 'category']
    search_fields = ['title', 'category__title']
    
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [UserReadOnlyPermission()]
        return [ManagerPermission()]
        
            
class SingleMenuItemViews(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [UserReadOnlyPermission()]
        return [ManagerPermission()]
    
    
class AllManagerViews(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [ManagerPermission]
    
    def get_queryset(self):
        manager_users = User.objects.filter(groups__name='Manager')
        return manager_users
    
    def add_manager(self, serializer, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists():
            return Response({"message": "Only Managers can add users to the Manager group."}, status=status.HTTP_403_FORBIDDEN)
        manager_users = Group.objects.get_or_create(name='Manager')[0]
        user = serializer.instance
        user.groups.add(manager_users)
        serializer.save()
        return Response({"message": f"{user.username} added to the Manager group."}, status=status.HTTP_201_CREATED)
        
    
class SingleManagerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [ManagerPermission]
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user is None:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"message": "Delete successful"}, status=status.HTTP_204_NO_CONTENT)
    

class DeliveryCrewView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [ManagerPermission]
    
    def get_queryset(self):
        delivery_crew = User.objects.filter(groups__name='Delivery-crew')
        return delivery_crew
    

class SingleDeliveryCrewView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(groups__name='Delivery-crew')
    serializer_class = UserSerializer
    permission_classes = [ManagerPermission]
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user is None:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"message": "Delete successful"}, status=status.HTTP_204_NO_CONTENT)
    
class CartViews(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
   
    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def perform_create(self, serializer):
        id = self.request.data.get('menuitem')
        quantity = int(self.request.data.get('quantity'))

        try:
            menuitem = MenuItem.objects.get(pk=id)
        except MenuItem.DoesNotExist:
            return Response({"message": "The specified MenuItem does not exist."}, status=status.HTTP_404_NOT_FOUND)

        user = self.request.user

        try:
            cart_item = Cart.objects.get(menuitem=menuitem, user=user)
            cart_item.quantity += quantity
            cart_item.price = cart_item.unit_price * cart_item.quantity
            cart_item.save()
        except Cart.DoesNotExist:
            unit_price = menuitem.price
            total_price = unit_price * quantity
            serializer.save(user=user, menuitem=menuitem, price=total_price)

    def delete(self, request):
        user = self.request.user
        Cart.objects.filter(user=user).delete()
        return Response({"message": "menuitems in cart successfully deleted"}, status=status.HTTP_204_NO_CONTENT)

class OrderViews(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user)
        total = self.calculate_total(cart_items)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user, total=total)

        for cart_item in cart_items:
            OrderItem.objects.create(
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price,
                order=order
            )
            cart_item.delete()
    
        return Response(
                data={'message': 'Order created successfully'},
                status=status.HTTP_201_CREATED
            )

    def calculate_total(self, cart_items):
        total = Decimal(0)
        for item in cart_items:
            total += item.price
        return total
    

class OrderItemViews(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
        