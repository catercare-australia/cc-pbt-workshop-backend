import pytest
from ex3_robustness.models import Order


@pytest.fixture
def draft_order(db):
    """Create a fresh DRAFT order in the database."""
    return Order.objects.create()
