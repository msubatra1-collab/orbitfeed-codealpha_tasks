from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def format_inr(value):
    """Format a numeric amount as rupees with Indian digit grouping."""
    try:
        amount = Decimal(str(value if value is not None else 0)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    except (InvalidOperation, TypeError, ValueError):
        amount = Decimal("0.00")

    sign = "-" if amount < 0 else ""
    whole, fraction = f"{abs(amount):.2f}".split(".")
    if len(whole) > 3:
        tail = whole[-3:]
        leading = whole[:-3]
        groups = []
        while leading:
            groups.append(leading[-2:])
            leading = leading[:-2]
        whole = ",".join(reversed(groups)) + "," + tail
    return f"{sign}₹{whole}.{fraction}"
