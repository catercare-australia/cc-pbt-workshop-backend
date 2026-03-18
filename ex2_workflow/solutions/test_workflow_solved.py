"""Exercise 2: SOLVED — Workflow Testing with State Machines"""
import pytest
from hypothesis import settings
from hypothesis.extra.django import from_field
from hypothesis.stateful import RuleBasedStateMachine, rule, precondition, initialize

pytestmark = pytest.mark.django_db(transaction=True)

from ex2_workflow.models import Order, OrderStatus, LineItem
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


class OrderWorkflowStateMachine(RuleBasedStateMachine):

    @initialize()
    def create_order(self):
        self.order = Order.objects.create()

    def assert_invariants(self):
        self.order.refresh_from_db()
        if self.order.status in (OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            assert self.order.payment_ref is not None
        if self.order.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            assert self.order.shipment_ref is not None
        if self.order.status == OrderStatus.CANCELLED:
            assert self.order.shipment_ref is None
        if self.order.status == OrderStatus.DRAFT:
            assert self.order.payment_ref is None
            assert self.order.shipment_ref is None

    # -- Allowed actions --

    @precondition(lambda self: self.order.status == OrderStatus.DRAFT)
    @rule(sku=st_sku, quantity=st_quantity, unit_price=st_unit_price)
    def action_add_item(self, sku, quantity, unit_price):
        count_before = self.order.items.count()
        self.order.add_item(sku, quantity, unit_price)
        self.order.refresh_from_db()
        assert self.order.items.count() == count_before + 1
        self.assert_invariants()

    @precondition(lambda self: self.order.status == OrderStatus.DRAFT and self.order.items.count() > 0)
    @rule()
    def action_submit(self):
        self.order.submit()
        self.order.refresh_from_db()
        assert self.order.status == OrderStatus.SUBMITTED
        self.assert_invariants()

    @precondition(lambda self: self.order.status == OrderStatus.SUBMITTED)
    @rule(ref=st_payment_ref)
    def action_pay(self, ref):
        self.order.pay(ref)
        self.order.refresh_from_db()
        assert self.order.status == OrderStatus.PAID
        assert self.order.payment_ref == ref
        self.assert_invariants()

    @precondition(lambda self: self.order.status == OrderStatus.PAID)
    @rule(ref=st_shipment_ref)
    def action_ship(self, ref):
        self.order.ship(ref)
        self.order.refresh_from_db()
        assert self.order.status == OrderStatus.SHIPPED
        assert self.order.shipment_ref == ref
        self.assert_invariants()

    @precondition(lambda self: self.order.status in (OrderStatus.DRAFT, OrderStatus.SUBMITTED))
    @rule()
    def action_cancel(self):
        self.order.cancel()
        self.order.refresh_from_db()
        assert self.order.status == OrderStatus.CANCELLED
        self.assert_invariants()

    # -- Forbidden actions --

    @precondition(lambda self: self.order.status not in (OrderStatus.DRAFT, OrderStatus.SUBMITTED))
    @rule()
    def action_cancel_forbidden(self):
        status_before = self.order.status
        try:
            self.order.cancel()
        except DomainError:
            pass  # Expected
        else:
            self.order.refresh_from_db()
            assert False, (
                f"cancel() should have been rejected from {status_before} "
                f"but succeeded, order is now {self.order.status}"
            )
        self.order.refresh_from_db()
        assert self.order.status == status_before, "State changed despite DomainError"

    @precondition(lambda self: self.order.status != OrderStatus.DRAFT)
    @rule(sku=st_sku, quantity=st_quantity, unit_price=st_unit_price)
    def action_add_item_forbidden(self, sku, quantity, unit_price):
        count_before = self.order.items.count()
        try:
            self.order.add_item(sku, quantity, unit_price)
        except DomainError:
            pass
        else:
            assert False, f"add_item() should have been rejected from {self.order.status}"
        assert self.order.items.count() == count_before

    @precondition(lambda self: self.order.status != OrderStatus.DRAFT or self.order.items.count() == 0)
    @rule()
    def action_submit_forbidden(self):
        status_before = self.order.status
        try:
            self.order.submit()
        except DomainError:
            pass
        else:
            assert False, f"submit() should have been rejected from {status_before}"
        self.order.refresh_from_db()
        assert self.order.status == status_before


TestOrderWorkflow = OrderWorkflowStateMachine.TestCase
TestOrderWorkflow.settings = settings(max_examples=50, stateful_step_count=10)
