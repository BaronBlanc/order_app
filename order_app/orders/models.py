from django.db import models


class Order(models.Model):
    marketplace = models.CharField(max_length=50)
    id_flux = models.CharField(max_length=50)
    order_status_marketplace = models.CharField(max_length=50, blank=True)
    order_status_lengow = models.CharField(max_length=50, blank=True)
    order_id = models.CharField(max_length=50, unique=True, primary_key=True)
    order_mrid = models.CharField(max_length=50, unique=True)
    order_refid = models.CharField(max_length=50, unique=True)
    order_external_id = models.CharField(max_length=50, blank=True)
    order_purchase_date = models.DateField(null=True)
    order_purchase_time = models.TimeField(null=True)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_tax = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    order_shipping = models.DecimalField(max_digits=10, decimal_places=2)
    order_commission = models.DecimalField(max_digits=10, decimal_places=2)
    order_processing_fee = models.DecimalField(max_digits=10, decimal_places=2)
    order_currency = models.CharField(max_length=10)
    payment_checkout = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=50, blank=True)
    payment_type = models.CharField(max_length=50, blank=True)
    payment_date = models.DateField(blank=True, null=True)
    payment_time = models.TimeField(blank=True, null=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    invoice_url = models.URLField(blank=True)
    billing_society = models.CharField(max_length=100, blank=True)
    billing_civility = models.CharField(max_length=50, blank=True)
    billing_lastname = models.CharField(max_length=100)
    billing_firstname = models.CharField(max_length=100, blank=True)
    billing_email = models.EmailField()
    billing_address = models.CharField(max_length=255, blank=True)
    billing_address_2 = models.CharField(max_length=255, blank=True)
    billing_address_complement = models.CharField(max_length=255, blank=True)
    billing_zipcode = models.CharField(max_length=20)
    billing_city = models.CharField(max_length=100)
    billing_country = models.CharField(max_length=100)
    billing_country_iso = models.CharField(max_length=10, blank=True)
    billing_phone_home = models.CharField(max_length=20, blank=True)
    billing_phone_office = models.CharField(max_length=20, blank=True)
    billing_phone_mobile = models.CharField(max_length=20, blank=True)
    billing_full_address = models.TextField()
    delivery_society = models.CharField(max_length=100, blank=True)
    delivery_civility = models.CharField(max_length=50, blank=True)
    delivery_lastname = models.CharField(max_length=100, blank=True)
    delivery_firstname = models.CharField(max_length=100, blank=True)
    delivery_email = models.EmailField(blank=True)
    delivery_address = models.CharField(max_length=255, blank=True)
    delivery_address_2 = models.CharField(max_length=255, blank=True)
    delivery_address_complement = models.CharField(max_length=255, blank=True)
    delivery_zipcode = models.CharField(max_length=20)
    delivery_city = models.CharField(max_length=100)
    delivery_country = models.CharField(max_length=100)
    delivery_country_iso = models.CharField(max_length=10, blank=True)
    delivery_phone_home = models.CharField(max_length=20, blank=True)
    delivery_phone_office = models.CharField(max_length=20, blank=True)
    delivery_phone_mobile = models.CharField(max_length=20, blank=True)
    delivery_full_address = models.TextField()
    tracking_method = models.CharField(max_length=50, blank=True)
    tracking_carrier = models.CharField(max_length=50, blank=True)
    tracking_number = models.CharField(max_length=50, blank=True)
    tracking_url = models.URLField(blank=True)
    tracking_shipped_date = models.DateTimeField(blank=True, null=True)
    tracking_relay = models.CharField(max_length=50, blank=True)
    tracking_delivering_by_marketplace = models.BooleanField(default=False)
    tracking_parcel_weight = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    order_comments = models.TextField(blank=True)
    customer_id = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Order {self.order_id} from {self.marketplace}"
