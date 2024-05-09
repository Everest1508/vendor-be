from django.urls import path
from .views import VendorListCreateAPIView,VendorDetailView,PurchaseOrderListCreateView,PurchaseOrderDetailView,VendorPerformanceViewSet,AssignVendorToPOAPIView
urlpatterns = [
    path("vendors/",VendorListCreateAPIView.as_view()),
    path("vendors/<int:vendor_id>/",VendorDetailView.as_view()),
    path("purchase-orders/", PurchaseOrderListCreateView.as_view()),
    path("purchase-orders/assign/", AssignVendorToPOAPIView.as_view()),
    path("purchase-orders/<int:po_id>/", PurchaseOrderDetailView.as_view()),
    path("purchase_orders/<int:pk>/acknowledge/", VendorPerformanceViewSet.as_view({'post': 'update_acknowledgment'})),
    path("vendors/<int:pk>/performance/", VendorPerformanceViewSet.as_view({'get': 'retrieve'})),
]
