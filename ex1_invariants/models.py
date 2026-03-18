from django.db import models

from shared.exceptions import DomainError


class OrderStatus(models.TextChoices):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(models.Model):
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.DRAFT,
    )
    payment_ref = models.CharField(max_length=100, blank=True, null=True)
    shipment_ref = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "ex1_invariants"

    def __str__(self):
        return f"Order #{self.pk} ({self.status})"

    # -- Domain logic (system under test — DO NOT EDIT) --

    def add_item(self, sku, quantity, unit_price):
        """Add a line item. Only allowed in DRAFT status."""
        if self.status != OrderStatus.DRAFT:
            raise DomainError("Can only add items to DRAFT orders")
        return LineItem.objects.create(
            order=self, sku=sku, quantity=quantity, unit_price=unit_price
        )

    def submit(self):
        """Submit the order. Only allowed in DRAFT with at least one item."""
        if self.status != OrderStatus.DRAFT:
            raise DomainError("Can only submit DRAFT orders")
        if self.items.count() == 0:
            raise DomainError("Cannot submit order with no items")
        self.status = OrderStatus.SUBMITTED
        self.save()

    def pay(self, payment_ref):
        """Record payment. Only allowed in SUBMITTED status."""
        if self.status != OrderStatus.SUBMITTED:
            raise DomainError("Can only pay SUBMITTED orders")
        self.status = OrderStatus.PAID
        self.payment_ref = payment_ref
        self.save()

    def ship(self, shipment_ref):
        """Record shipment. Only allowed in PAID status."""
        if self.status != OrderStatus.PAID:
            raise DomainError("Can only ship PAID orders")
        self.status = OrderStatus.SHIPPED
        self.shipment_ref = shipment_ref
        self.save()

    def cancel(self):
        """Cancel the order. Only allowed in DRAFT or SUBMITTED status."""
        if self.status not in (OrderStatus.DRAFT, OrderStatus.SUBMITTED):
            raise DomainError("Can only cancel DRAFT or SUBMITTED orders")
        self.status = OrderStatus.CANCELLED
        self.payment_ref = None
        self.shipment_ref = None
        self.save()



class LineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    sku = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        app_label = "ex1_invariants"

    def __str__(self):
        return f"{self.sku} x{self.quantity} @ {self.unit_price}"
