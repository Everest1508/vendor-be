from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
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
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True)
    items = models.JSONField() 
    quantity = models.IntegerField()
    status = models.CharField(max_length=50)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(null=True)
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"PO {self.po_number} - {self.vendor.name}"
    
    def save(self, *args, **kwargs):
        if self.vendor_id is not None and self.issue_date is None:
            self.issue_date = timezone.now()
        super().save(*args, **kwargs)

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField(null=True)
    quality_rating_avg = models.FloatField(null= True)
    average_response_time = models.FloatField(null=True)
    fulfillment_rate = models.FloatField(null= True)

    def __str__(self):
        return f"{self.vendor.name} - {self.date}"
    


@receiver(post_save, sender=PurchaseOrder)
def update_performance_metrics(sender, instance, created, **kwargs):
    if instance.status == 'completed':
        update_on_time_delivery_rate(instance.vendor)
        
    if instance.quality_rating is not None:
        update_quality_rating_avg(instance.vendor)
        
    if instance.status != 'acknowledged':
        update_fulfillment_rate(instance.vendor)

@receiver(pre_save, sender=PurchaseOrder)
def update_acknowledgment_date(sender, instance, **kwargs):
    if instance.status == 'acknowledged' and not instance.acknowledgment_date:
        instance.acknowledgment_date = timezone.now()

@receiver(post_save, sender=Vendor)
def update_vendor_performance(sender, instance, created, **kwargs):
    update_historical_performance(instance)

def update_on_time_delivery_rate(vendor):
    completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
    on_time_deliveries = completed_pos.filter(delivery_date__lte=timezone.now())
    total_completed_pos = completed_pos.count()
    if total_completed_pos > 0:
        on_time_delivery_rate = on_time_deliveries.count() / total_completed_pos
        vendor.on_time_delivery_rate = on_time_delivery_rate
        vendor.save()

        HistoricalPerformance.objects.create(
            vendor=vendor,
            date=timezone.now(),
            on_time_delivery_rate=vendor.on_time_delivery_rate,
            quality_rating_avg=vendor.quality_rating_avg,
            average_response_time=vendor.average_response_time,
            fulfillment_rate=vendor.fulfillment_rate
        )

def update_quality_rating_avg(vendor):
    completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed', quality_rating__isnull=False)
    quality_ratings = completed_pos.values_list('quality_rating', flat=True)
    if quality_ratings:
        quality_rating_avg = sum(quality_ratings) / len(quality_ratings)
        vendor.quality_rating_avg = quality_rating_avg
        vendor.save()

        HistoricalPerformance.objects.create(
            vendor=vendor,
            date=timezone.now(),
            on_time_delivery_rate=vendor.on_time_delivery_rate,
            quality_rating_avg=vendor.quality_rating_avg,
            average_response_time=vendor.average_response_time,
            fulfillment_rate=vendor.fulfillment_rate
        )

def update_fulfillment_rate(vendor):
    total_pos = PurchaseOrder.objects.filter(vendor=vendor).count()
    completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed').count()
    if total_pos > 0:
        fulfillment_rate = completed_pos / total_pos
        vendor.fulfillment_rate = fulfillment_rate
        vendor.save()

        HistoricalPerformance.objects.create(
            vendor=vendor,
            date=timezone.now(),
            on_time_delivery_rate=vendor.on_time_delivery_rate,
            quality_rating_avg=vendor.quality_rating_avg,
            average_response_time=vendor.average_response_time,
            fulfillment_rate=vendor.fulfillment_rate
        )

def update_historical_performance(vendor):
    HistoricalPerformance.objects.create(
        vendor=vendor,
        date=timezone.now(),
        on_time_delivery_rate=vendor.on_time_delivery_rate,
        quality_rating_avg=vendor.quality_rating_avg,
        average_response_time=vendor.average_response_time,
        fulfillment_rate=vendor.fulfillment_rate
    )