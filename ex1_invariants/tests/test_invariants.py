"""
Exercise 1: Invariant Properties
=================================
Write properties that must ALWAYS hold for any valid Order state.

These are "business rules encoded as truth" — if they fail, something
is wrong with the domain logic.

Strategies are derived from Django model field definitions via from_field()
— the model IS the source of truth for valid test data.

Run: pytest ex1_invariants/tests/test_invariants.py -v
"""
import pytest
from hypothesis import given, settings
from hypothesis.extra.django import from_field

from ex1_invariants.models import Order, OrderStatus, LineItem
from shared.exceptions import DomainError

# Strategies derived from model fields
st_sku = from_field(LineItem._meta.get_field("sku"))
st_quantity = from_field(LineItem._meta.get_field("quantity"))
st_unit_price = from_field(LineItem._meta.get_field("unit_price"))
st_payment_ref = from_field(Order._meta.get_field("payment_ref")).filter(
    lambda x: x is not None and x != ""
)


@pytest.mark.django_db
class TestOrderInvariants:
    """Property-based tests for Order invariants."""

    @given(sku=st_sku, quantity=st_quantity, unit_price=st_unit_price)
    @settings(max_examples=50)
    def test_draft_order_has_no_refs(self, sku, quantity, unit_price):
        """
        TODO: A newly created DRAFT order should have no payment or shipment refs,
        even after adding items.

        Steps:
        1. Create a fresh Order
        2. Add an item using order.add_item(sku, quantity, unit_price)
        3. Reload from DB: order.refresh_from_db()
        4. Assert payment_ref is None and shipment_ref is None
        """
        pass

    @given(sku=st_sku, quantity=st_quantity, unit_price=st_unit_price)
    @settings(max_examples=50)
    def test_items_immutable_after_submit(self, sku, quantity, unit_price):
        """
        TODO: Once an order is submitted, adding items should raise DomainError.

        Steps:
        1. Create an Order, add one item, submit it
        2. Try to add another item using order.add_item(sku, quantity, unit_price)
        3. Assert DomainError is raised
        """
        pass

    @given(
        sku=st_sku,
        quantity=st_quantity,
        unit_price=st_unit_price,
        payment_ref=st_payment_ref,
    )
    @settings(max_examples=50)
    def test_paid_order_has_payment_ref(self, sku, quantity, unit_price, payment_ref):
        """
        TODO: After paying, the order must have a payment_ref and correct status.

        Steps:
        1. Create Order -> add item -> submit -> order.pay(payment_ref)
        2. Reload from DB
        3. Assert status is PAID
        4. Assert payment_ref is not None
        5. Assert shipment_ref is None (not shipped yet)
        """
        pass

    @given(sku=st_sku, quantity=st_quantity, unit_price=st_unit_price)
    @settings(max_examples=50)
    def test_cancelled_order_invariants(self, sku, quantity, unit_price):
        """
        TODO: A cancelled order should have no shipment_ref.

        Steps:
        1. Create Order -> add item -> submit
        2. Cancel it: order.cancel()
        3. Reload from DB
        4. Assert status is CANCELLED
        5. Assert shipment_ref is None
        """
        pass
