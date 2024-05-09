from django.urls import path
from .views import VendorListCreateAPIView,VendorDetailView,PurchaseOrderListCreateView,PurchaseOrderDetailView,VendorPerformanceViewSet
urlpatterns = [
    path("vendors/",VendorListCreateAPIView.as_view(),name="list-create-vendors"),
    path("vendors/<int:vendor_id>/",VendorDetailView.as_view(),name="detail-vendors"),
    path("purchase-orders/", PurchaseOrderListCreateView.as_view()),
    path("purchase-orders/<int:po_id>/", PurchaseOrderDetailView.as_view()),
    path('api/purchase_orders/<int:pk>/acknowledge/', VendorPerformanceViewSet.as_view({'post': 'update_acknowledgment'}), name='acknowledge-po'),
    path('api/vendors/<int:pk>/performance/', VendorPerformanceViewSet.as_view({'get': 'retrieve'}), name='vendor-performance'),
]
