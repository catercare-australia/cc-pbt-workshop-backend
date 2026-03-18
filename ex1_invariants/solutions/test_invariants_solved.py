"""Exercise 1: SOLVED — Invariant Properties"""
import pytest
from decimal import Decimal
from hypothesis import given, settings
from hypothesis.extra.django import from_field

from ex1_invariants.models import Order, OrderStatus, LineItem
from shared.exceptions import DomainError

st_sku = from_field(LineItem._meta.get_field("sku"))
st_quantity = from_field(LineItem._meta.get_field("quantity"))
st_unit_price = from_field(LineItem._meta.get_field("unit_price"))
st_payment_ref = from_field(Order._meta.get_field("payment_ref")).filter(
    lambda x: x is not None and x != ""
)


@pytest.mark.django_db
class TestOrderInvariants:

    @given(sku=st_sku, quantity=st_quantity, unit_price=st_unit_price)
    @settings(max_examples=50)
    def test_draft_order_has_no_refs(self, sku, quantity, unit_price):
        order = Order.objects.create()
        order.add_item(sku, quantity, unit_price)
        order.refresh_from_db()
        assert order.payment_ref is None
        assert order.shipment_ref is None

    @given(sku=st_sku, quantity=st_quantity, unit_price=st_unit_price)
    @settings(max_examples=50)
    def test_items_immutable_after_submit(self, sku, quantity, unit_price):
        order = Order.objects.create()
        order.add_item("SKU-INIT-001", 1, Decimal("10.00"))
        order.submit()
        order.refresh_from_db()
        with pytest.raises(DomainError):
            order.add_item(sku, quantity, unit_price)

    @given(
        sku=st_sku,
        quantity=st_quantity,
        unit_price=st_unit_price,
        payment_ref=st_payment_ref,
    )
    @settings(max_examples=50)
    def test_paid_order_has_payment_ref(self, sku, quantity, unit_price, payment_ref):
        order = Order.objects.create()
        order.add_item(sku, quantity, unit_price)
        order.submit()
        order.pay(payment_ref)
        order.refresh_from_db()
        assert order.status == OrderStatus.PAID
        assert order.payment_ref is not None
        assert order.shipment_ref is None

    @given(sku=st_sku, quantity=st_quantity, unit_price=st_unit_price)
    @settings(max_examples=50)
    def test_cancelled_order_invariants(self, sku, quantity, unit_price):
        order = Order.objects.create()
        order.add_item(sku, quantity, unit_price)
        order.submit()
        order.cancel()
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED
        assert order.shipment_ref is None
