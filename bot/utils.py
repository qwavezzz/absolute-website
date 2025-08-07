import uuid

def generate_order_id() -> str:
    """Generate short unique order ID."""
    return uuid.uuid4().hex[:5].upper()
