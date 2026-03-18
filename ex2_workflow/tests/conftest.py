import pytest
from ex2_workflow.models import Order


@pytest.fixture
def draft_order(db):
    """Create a fresh DRAFT order in the database."""
    return Order.objects.create()
