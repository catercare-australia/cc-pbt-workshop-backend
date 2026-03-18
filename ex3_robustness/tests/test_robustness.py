"""
Exercise 3: Robustness Properties
===================================
Verify that domain operations never crash unexpectedly —
they should either succeed or raise DomainError, never anything else.

This tests resilience: no matter what valid-ish inputs we throw at the
domain functions, they must never raise TypeError, AttributeError, or
any other unexpected exception.

from_model(Order, status=...) generates complete saved Order instances.
from_field() generates valid values for individual model fields.
The "..." (Ellipsis) forces Hypothesis to generate random statuses
instead of always using the default (DRAFT).

Run: pytest ex3_robustness/tests/test_robustness.py -v
"""
import pytest
from hypothesis import given, settings
from hypothesis.extra.django import from_model, from_field

from ex3_robustness.models import Order, LineItem
from shared.exceptions import DomainError

# Strategies derived from model fields
st_sku = from_field(LineItem._meta.get_field("sku"))
st_quantity = from_field(LineItem._meta.get_field("quantity"))
st_unit_price = from_field(LineItem._meta.get_field("unit_price"))
st_payment_ref = from_field(Order._meta.get_field("payment_ref")).filter(
    lambda x: x is not None and x != ""
)
st_shipment_ref = from_field(Order._meta.get_field("shipment_ref")).filter(
    lambda x: x is not None and x != ""
)


@pytest.mark.django_db
class TestRobustness:
    """No domain operation should ever raise an unexpected exception."""

    @given(
        order=from_model(Order, status=...),
        sku=st_sku,
        quantity=st_quantity,
        unit_price=st_unit_price,
    )
    @settings(max_examples=100)
    def test_add_item_never_crashes(self, order, sku, quantity, unit_price):
        """
        TODO: Call order.add_item(sku, quantity, unit_price).
        Assert it either succeeds or raises DomainError — never
        TypeError, AttributeError, or any other unexpected exception.

        Hint:
            try:
                order.add_item(sku, quantity, unit_price)
            except DomainError:
                pass  # Expected for non-DRAFT
            # If any OTHER exception propagates, the test fails automatically
        """
        pass

    @given(order=from_model(Order, status=...))
    @settings(max_examples=50)
    def test_submit_never_crashes(self, order):
        """
        TODO: Call order.submit().
        Assert only DomainError or success.
        """
        pass

    @given(order=from_model(Order, status=...), payment_ref=st_payment_ref)
    @settings(max_examples=50)
    def test_pay_never_crashes(self, order, payment_ref):
        """
        TODO: Call order.pay(payment_ref).
        Assert only DomainError or success.
        """
        pass

    @given(order=from_model(Order, status=...), shipment_ref=st_shipment_ref)
    @settings(max_examples=50)
    def test_ship_never_crashes(self, order, shipment_ref):
        """
        TODO: Call order.ship(shipment_ref).
        Assert only DomainError or success.
        """
        pass

    @given(order=from_model(Order, status=...))
    @settings(max_examples=50)
    def test_cancel_never_crashes(self, order):
        """
        TODO: Call order.cancel().
        Assert only DomainError or success.
        """
        pass
