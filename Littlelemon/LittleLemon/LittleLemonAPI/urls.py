from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('category', views.CategoriesView.as_view()),
    path('menuitems', views.MenuItemViews.as_view()),
    path('menuitems/<int:pk>', views.SingleMenuItemViews.as_view()),
    path('groups/managers/users', views.AllManagerViews.as_view()),
    path('groups/managers/users/<int:pk>', views.SingleManagerView.as_view()),
    path('groups/deliver-crew/users', views.DeliveryCrewView.as_view()),
    path('groups/deliver-crew/users/<int:pk>', views.SingleDeliveryCrewView.as_view()),
    path('api-token-auth', obtain_auth_token),
    path('orders', views.OrderViews.as_view()),
    path('orders/<int:pk>', views.OrderItemViews.as_view()),
    path('cart/menu-items', views.CartViews.as_view()),
]