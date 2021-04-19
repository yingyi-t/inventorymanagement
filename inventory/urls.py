from django.urls import include, path
from rest_framework.routers import DefaultRouter

from inventory import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', views.UserViewSet, 'users')
router.register(r'stores', views.StoreViewSet, 'stores')
router.register(r'material-stocks', views.MaterialStockViewSet, 'material_stocks')
router.register(r'materials', views.MaterialViewSet, 'materials')
router.register(
    r'material-quantities', views.MaterialQuantityViewSet, 'material-quantities'
)
router.register(r'products', views.ProductViewSet, 'products')
router.register(r'inventory', views.InventoryViewSet, 'inventory')
router.register(r'product-capacity', views.ProductCapacityViewSet, 'product-capacity')
router.register(r'restock', views.RestockViewSet, 'restock')
router.register(r'sales', views.SalesViewSet, 'sales')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
