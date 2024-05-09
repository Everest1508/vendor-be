from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PurchaseOrder, HistoricalPerformance
from django.db import models

class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True,null=True,blank=True)
    on_time_delivery_rate = models.FloatField(null=True,blank=True)
    quality_rating_avg = models.FloatField(null=True,blank=True)
    average_response_time = models.FloatField(null=True,blank=True)
    fulfillment_rate = models.FloatField(null=True,blank=True)

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField() 
    quantity = models.IntegerField()
    status = models.CharField(max_length=50)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField()
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"PO {self.po_number} - {self.vendor.name}"

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

    def __str__(self):
        return f"{self.vendor.name} - {self.date}"
    


@receiver(post_save, sender=PurchaseOrder)
def update_performance_metrics(sender, instance, created, **kwargs):
    if instance.status == 'completed':
        update_on_time_delivery_rate(instance.vendor)
        
    if instance.quality_rating is not None:
        update_quality_rating_avg(instance.vendor)

@receiver(pre_save, sender=PurchaseOrder)
def update_acknowledgment_date(sender, instance, **kwargs):
    if instance.status == 'acknowledged' and not instance.acknowledgment_date:
        instance.acknowledgment_date = timezone.now()

def update_on_time_delivery_rate(vendor):
    completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
    on_time_deliveries = completed_pos.filter(delivery_date__lte=timezone.now())
    total_completed_pos = completed_pos.count()
    if total_completed_pos > 0:
        on_time_delivery_rate = on_time_deliveries.count() / total_completed_pos
        vendor.on_time_delivery_rate = on_time_delivery_rate
        vendor.save()

def update_quality_rating_avg(vendor):
    completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed', quality_rating__isnull=False)
    quality_ratings = completed_pos.values_list('quality_rating', flat=True)
    if quality_ratings:
        quality_rating_avg = sum(quality_ratings) / len(quality_ratings)
        vendor.quality_rating_avg = quality_rating_avg
        vendor.save()
