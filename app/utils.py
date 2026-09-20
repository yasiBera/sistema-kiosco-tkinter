from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def parse_price_to_cents(value: str) -> int:
    """Convierte entradas como 1500,50 o 1.500,50 a centavos."""
    cleaned = value.strip().replace("$", "").replace(" ", "")
    if not cleaned:
        raise ValueError("El precio es obligatorio.")

    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif cleaned.count(".") > 1:
        cleaned = cleaned.replace(".", "")
    elif cleaned.count(".") == 1:
        _whole, decimals = cleaned.split(".")
        if len(decimals) == 3:
            cleaned = cleaned.replace(".", "")

    try:
        amount = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError("Ingresá un precio válido.") from exc

    if amount < 0:
        raise ValueError("El precio no puede ser negativo.")

    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def format_currency(cents: int) -> str:
    amount = Decimal(cents) / 100
    integer_part, decimal_part = f"{amount:.2f}".split(".")
    groups = []
    while integer_part:
        groups.append(integer_part[-3:])
        integer_part = integer_part[:-3]
    return f"$ {'.'.join(reversed(groups))},{decimal_part}"
