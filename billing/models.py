from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    product_id = models.CharField(max_length=50, unique=True)
    available_stocks = models.IntegerField()
    price = models.FloatField()
    tax_percentage = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.product_id})"

class Bill(models.Model):
    customer_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount_without_tax = models.FloatField(default=0.0)
    total_tax_payable = models.FloatField(default=0.0)
    net_price = models.FloatField(default=0.0)
    amount_paid = models.FloatField(default=0.0)
    balance_amount = models.FloatField(default=0.0)
    balance_denomination_breakdown = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Bill #{self.id} for {self.customer_email}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    tax_percentage = models.FloatField()
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price * (1 + self.tax_percentage / 100)

    @property
    def base_price(self):
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        return self.quantity * self.unit_price * (self.tax_percentage / 100)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
