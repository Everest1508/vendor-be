from django.urls import path
from .views import VendorListCreateAPIView,VendorDetailView,PurchaseOrderListCreateView,PurchaseOrderDetailView
urlpatterns = [
    path("vendors/",VendorListCreateAPIView.as_view(),name="list-create-vendors"),
    path("vendors/<int:vendor_id>/",VendorDetailView.as_view(),name="detail-vendors"),
    path("purchase-orders/", PurchaseOrderListCreateView.as_view()),
    path("purchase-orders/<int:po_id>/", PurchaseOrderDetailView.as_view()),
]
