"""Exercise 3: SOLVED — Robustness Properties"""
import pytest
from hypothesis import given, settings
from hypothesis.extra.django import from_model, from_field

from ex3_robustness.models import Order, LineItem
from shared.exceptions import DomainError

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

    @given(
        order=from_model(Order, status=...),
        sku=st_sku,
        quantity=st_quantity,
        unit_price=st_unit_price,
    )
    @settings(max_examples=100)
    def test_add_item_never_crashes(self, order, sku, quantity, unit_price):
        try:
            order.add_item(sku, quantity, unit_price)
        except DomainError:
            pass

    @given(order=from_model(Order, status=...))
    @settings(max_examples=50)
    def test_submit_never_crashes(self, order):
        try:
            order.submit()
        except DomainError:
            pass

    @given(order=from_model(Order, status=...), payment_ref=st_payment_ref)
    @settings(max_examples=50)
    def test_pay_never_crashes(self, order, payment_ref):
        try:
            order.pay(payment_ref)
        except DomainError:
            pass

    @given(order=from_model(Order, status=...), shipment_ref=st_shipment_ref)
    @settings(max_examples=50)
    def test_ship_never_crashes(self, order, shipment_ref):
        try:
            order.ship(shipment_ref)
        except DomainError:
            pass

    @given(order=from_model(Order, status=...))
    @settings(max_examples=50)
    def test_cancel_never_crashes(self, order):
        try:
            order.cancel()
        except DomainError:
            pass
