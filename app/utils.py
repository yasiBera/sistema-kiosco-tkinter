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

    if not amount.is_finite():
        raise ValueError("El precio debe ser un número finito.")
    if amount < 0:
        raise ValueError("El precio no puede ser negativo.")

    try:
        rounded_cents = (amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise ValueError("Ingresá un precio válido.") from exc
    return int(rounded_cents)


def parse_markup_percent(value: str) -> int:
    """Valida el porcentaje entero que se agrega al costo."""
    cleaned = value.strip().replace("%", "")
    if not cleaned:
        raise ValueError("El porcentaje de recargo es obligatorio.")
    try:
        percentage = int(cleaned)
    except ValueError as exc:
        raise ValueError("El porcentaje debe ser un número entero.") from exc
    if percentage < 0:
        raise ValueError("El porcentaje no puede ser negativo.")
    return percentage


def calculate_price_with_markup(cost_cents: int, markup_percent: int) -> tuple[int, int]:
    """Devuelve precio de venta y ganancia en centavos aplicando recargo al costo."""
    if cost_cents < 0 or markup_percent < 0:
        raise ValueError("El costo y el porcentaje no pueden ser negativos.")
    # All amounts are non-negative cents. Adding 50 before integer division
    # rounds half-cent ties upward, matching ROUND_HALF_UP.
    sale_price = (cost_cents * (100 + markup_percent) + 50) // 100
    return sale_price, sale_price - cost_cents


def format_currency(cents: int) -> str:
    amount = Decimal(cents) / 100
    integer_part, decimal_part = f"{amount:.2f}".split(".")
    groups = []
    while integer_part:
        groups.append(integer_part[-3:])
        integer_part = integer_part[:-3]
    return f"$ {'.'.join(reversed(groups))},{decimal_part}"
