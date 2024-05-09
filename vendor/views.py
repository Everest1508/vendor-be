from django.shortcuts import get_object_or_404
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Vendor,PurchaseOrder,HistoricalPerformance
from .serializers import VendorSerializer,VendorPerformanceSerializer,PurchaseOrderSerializer,AssignVendorToPOSerializer

class VendorListCreateAPIView(APIView):
    def get(self,request):
        serializer = VendorSerializer(Vendor.objects.all(),many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        else:
            return Response(serializer.errors)
        
class VendorDetailView(APIView):
    def get(self, request, vendor_id):
        try:
            vendor = Vendor.objects.get(pk=vendor_id)
            serializer = VendorSerializer(vendor)
            return Response(serializer.data)
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, vendor_id):
        try:
            vendor = Vendor.objects.get(pk=vendor_id)
            serializer = VendorSerializer(vendor, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, vendor_id):
        try:
            vendor = Vendor.objects.get(pk=vendor_id)
            vendor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class PurchaseOrderListCreateView(APIView):
    def get(self, request):
        vendor_id = request.query_params.get('vendor', None)
        if vendor_id:
            purchase_orders = PurchaseOrder.objects.filter(vendor_id=vendor_id)
        else:
            purchase_orders = PurchaseOrder.objects.all()
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PurchaseOrderDetailView(APIView):
    def get(self, request, po_id):
        try:
            purchase_order = PurchaseOrder.objects.get(pk=po_id)
            serializer = PurchaseOrderSerializer(purchase_order)
            return Response(serializer.data)
        except PurchaseOrder.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, po_id):
        try:
            purchase_order = PurchaseOrder.objects.get(pk=po_id)
            serializer = PurchaseOrderSerializer(purchase_order, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PurchaseOrder.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, po_id):
        try:
            purchase_order = PurchaseOrder.objects.get(pk=po_id)
            purchase_order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PurchaseOrder.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class VendorPerformanceViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        vendor = get_object_or_404(Vendor, pk=pk)
        serializer = VendorPerformanceSerializer(vendor)
        return Response(serializer.data)

    def update_acknowledgment(self, request, pk=None):
        po_id = request.data.get('po_id')
        po = get_object_or_404(PurchaseOrder, pk=po_id)
        po.status = 'acknowledged'
        po.acknowledgment_date = timezone.now()
        po.save()
        return Response("Acknowledgment updated successfully", status=status.HTTP_200_OK)

class AssignVendorToPOAPIView(APIView):
    def post(self, request):
        serializer = AssignVendorToPOSerializer(data=request.data)
        if serializer.is_valid():
            po_id = serializer.validated_data.get('po_id')
            vendor_id = serializer.validated_data.get('vendor_id')
            
            po = get_object_or_404(PurchaseOrder, pk=po_id)
            vendor = get_object_or_404(Vendor, pk=vendor_id)

            po.vendor = vendor
            po.save()

            return Response("Vendor assigned to purchase order successfully", status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)