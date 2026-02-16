def depreciation_curve(purchase_price: float, years: int) -> float:
    """
    Simple, credible hackathon curve (total depreciation over N years).
    Year 1: 18%, Year 2: 12%, Year 3: 10%, Year 4+: 8%
    """
    rates = []
    if years >= 1: rates.append(0.18)
    if years >= 2: rates.append(0.12)
    if years >= 3: rates.append(0.10)
    for _ in range(max(0, years - 3)):
        rates.append(0.08)

    remaining = purchase_price
    dep_total = 0.0
    for r in rates[:years]:
        dep = remaining * r
        dep_total += dep
        remaining -= dep
    return dep_total
