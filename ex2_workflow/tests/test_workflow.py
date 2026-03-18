"""
Exercise 2: Workflow Testing with State Machines
=================================================
Build a state machine that generates random action sequences,
runs them against the real system, and verifies the correct
transition rules are enforced.

Each rule's @precondition encodes what SHOULD be allowed.
The "forbidden" rules verify that invalid transitions are rejected.
If the real code disagrees with your preconditions, you've found a bug.

Strategies are derived from Django model field definitions via from_field()
— the model IS the source of truth for valid test data.

Run: pytest ex2_workflow/tests/test_workflow.py -v
"""
import pytest
from hypothesis import settings
from hypothesis.extra.django import from_field
from hypothesis.stateful import RuleBasedStateMachine, rule, precondition, initialize

pytestmark = pytest.mark.django_db(transaction=True)

from ex2_workflow.models import Order, OrderStatus, LineItem
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


class OrderWorkflowStateMachine(RuleBasedStateMachine):
    """
    State machine that generates random sequences of Order actions.

    Each rule's @precondition encodes the correct business rule.
    The "allowed" rules verify the action succeeds as expected.
    The "forbidden" rules verify the action is rejected.
    """

    @initialize()
    def create_order(self):
        """Set up a fresh order."""
        self.order = Order.objects.create()

    def assert_invariants(self):
        """
        TODO: Assert invariants hold on the real order after every step.

        Check these after each action:
        1. If status in (PAID, SHIPPED, DELIVERED) -> payment_ref is not None
        2. If status in (SHIPPED, DELIVERED) -> shipment_ref is not None
        3. If status == CANCELLED -> shipment_ref is None
        4. If status == DRAFT -> payment_ref is None and shipment_ref is None
        """
        pass

    # -- Allowed action rules --
    # The precondition encodes when this action SHOULD be allowed.

    @precondition(lambda self: self.order.status == OrderStatus.DRAFT)
    @rule(sku=st_sku, quantity=st_quantity, unit_price=st_unit_price)
    def action_add_item(self, sku, quantity, unit_price):
        """
        TODO:
        1. Record item count before: self.order.items.count()
        2. Call self.order.add_item(sku, quantity, unit_price)
        3. Reload: self.order.refresh_from_db()
        4. Assert item count increased by 1
        5. Call self.assert_invariants()
        """
        pass

    @precondition(lambda self: self.order.status == OrderStatus.DRAFT and self.order.items.count() > 0)
    @rule()
    def action_submit(self):
        """
        TODO:
        1. Call self.order.submit()
        2. Reload: self.order.refresh_from_db()
        3. Assert status is SUBMITTED
        4. Call self.assert_invariants()
        """
        pass

    @precondition(lambda self: self.order.status == OrderStatus.SUBMITTED)
    @rule(ref=st_payment_ref)
    def action_pay(self, ref):
        """
        TODO:
        1. Call self.order.pay(ref)
        2. Reload and assert status is PAID
        3. Assert payment_ref == ref
        4. Call self.assert_invariants()
        """
        pass

    @precondition(lambda self: self.order.status == OrderStatus.PAID)
    @rule(ref=st_shipment_ref)
    def action_ship(self, ref):
        """
        TODO:
        1. Call self.order.ship(ref)
        2. Reload and assert status is SHIPPED
        3. Assert shipment_ref == ref
        4. Call self.assert_invariants()
        """
        pass

    @precondition(lambda self: self.order.status in (OrderStatus.DRAFT, OrderStatus.SUBMITTED))
    @rule()
    def action_cancel(self):
        """
        TODO:
        1. Call self.order.cancel()
        2. Reload and assert status is CANCELLED
        3. Call self.assert_invariants()
        """
        pass

    # -- Forbidden action rules --
    # These test that invalid transitions are properly rejected.
    # The precondition is the OPPOSITE of the allowed rule.
    #
    # In the rule body:
    # 1. Record status_before
    # 2. Try the action — expect DomainError
    # 3. If it SUCCEEDS instead, that's a bug!
    # 4. Assert state is unchanged
    #
    # TODO: Add forbidden rules for cancel, add_item, submit
    #
    # Hint for cancel_forbidden:
    #   @precondition(lambda self: self.order.status not in (OrderStatus.DRAFT, OrderStatus.SUBMITTED))
    #   @rule()
    #   def action_cancel_forbidden(self):
    #       ...


# This line makes pytest discover and run the state machine
TestOrderWorkflow = OrderWorkflowStateMachine.TestCase
TestOrderWorkflow.settings = settings(max_examples=30, stateful_step_count=10)
