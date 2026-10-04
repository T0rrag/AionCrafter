"""Pure deterministic economics in integer currency units and exact rational ratios."""
from dataclasses import dataclass
from fractions import Fraction

from .codec import require
from .identity import MarketScope, PriceIdentity, Tradability
from .models import FeeBasis, ItemQuantity, Money, PriceObservation, Recipe, exact


def units(amount: str, market: MarketScope) -> int:
    money = Money(amount, market.currency)
    require(money.decimal >= 0, "AMOUNT", "Price/fee must be nonnegative")
    return int(Fraction(amount) * 10 ** market.currency.decimal_places)


def amount(value: int, market: MarketScope) -> str:
    scale = market.currency.decimal_places
    sign = '-' if value < 0 else ''
    whole, tail = divmod(abs(value), 10 ** scale)
    return f'{sign}{whole}' + (f'.{tail:0{scale}d}' if scale else '')


@dataclass(frozen=True)
class SaleFees:
    tax_rate: str
    fixed: str
    rounding: str
    source: str

    def __post_init__(self):
        require(exact(self.tax_rate, 'tax rate') <= 1, 'TAX', 'Tax rate must be in [0,1]')
        exact(self.fixed, 'fixed fee')
        require(self.rounding in ('floor', 'ceil', 'half_up'), 'ROUNDING', 'Choose proceeds rounding explicitly')
        require(type(self.source) is str and bool(self.source.strip()), 'FEE_SOURCE', 'State the fee assumption/source')


@dataclass(frozen=True)
class MaterialLine:
    item: ItemQuantity
    observation: PriceObservation | None
    subtotal: int | None


@dataclass(frozen=True)
class MaterialsResult:
    lines: tuple[MaterialLine, ...]
    known_subtotal: int
    total: int | None
    missing: tuple[str, ...]


@dataclass(frozen=True)
class EconomicsResult:
    crafts: int
    produced: int
    planned_sales: int
    leftovers: int
    materials: MaterialsResult
    craft_cost: int | None
    proceeds: int | None
    profit: int | None
    roi_percent: Fraction | None
    break_even: Fraction | None
    minimum_break_even_price: int | None
    issues: tuple[str, ...]


def materials_cost(items: tuple[ItemQuantity, ...], market: MarketScope,
                   observations: tuple[PriceObservation, ...]) -> MaterialsResult:
    require(bool(items), 'QUANTITY', 'Select at least one material')
    require(market.resolved, 'UNRESOLVED_SCOPE', 'Select a complete market')
    prices = {}
    for obs in observations:
        require(obs.identity.market == market, 'SCOPE_MISMATCH', 'Observation market differs')
        require(obs.identity.item.key not in prices, 'DUPLICATE_PRICE', 'Select one observation per variant')
        prices[obs.identity.item.key] = obs
    merged = {}
    for entry in items:
        PriceIdentity(entry.item, market)
        prior = merged.get(entry.item.key)
        merged[entry.item.key] = ItemQuantity(entry.item, entry.quantity + (prior.quantity if prior else 0))
    lines, missing = [], []
    for key, entry in merged.items():
        obs = prices.get(key)
        require(obs is None or obs.acquisition_reference, 'PRICE_TYPE', 'Sell-back/completed sales cannot price acquisition')
        subtotal = None if obs is None or obs.unit_price is None else units(obs.unit_price, market) * entry.quantity
        if subtotal is None:
            missing.append(key)
        lines.append(MaterialLine(entry, obs, subtotal))
    known = sum(line.subtotal for line in lines if line.subtotal is not None)
    return MaterialsResult(tuple(lines), known, None if missing else known, tuple(missing))


def rounded(value: Fraction, rule: str) -> int:
    if rule == 'floor':
        return value.numerator // value.denominator
    if rule == 'ceil':
        return -(-value.numerator // value.denominator)
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)


def item_economics(recipe: Recipe, target: ItemQuantity, market: MarketScope,
                   observations: tuple[PriceObservation, ...], selling_price: str | None,
                   sale_fees: SaleFees, craft_fees=None) -> EconomicsResult:
    require(len(recipe.outcomes) == 1 and recipe.outcomes[0].probability is not None and Fraction(recipe.outcomes[0].probability) == 1,
            'NONDETERMINISTIC', 'Only a known deterministic outcome is supported in Phase 02')
    output = next((x for x in recipe.outcomes[0].outputs if x.item == target.item), None)
    require(output is not None, 'OUTPUT', 'Target must be an explicit recipe output')
    require(recipe.scope == target.item.scope, 'SCOPE_MISMATCH', 'Recipe/target scope differs')
    PriceIdentity(target.item, market)
    require(target.item.variant.tradability is Tradability.TRADEABLE, 'TRADABILITY', 'Output cannot be sold')
    crafts = (target.quantity + output.quantity - 1) // output.quantity
    produced = crafts * output.quantity
    materials = materials_cost(tuple(ItemQuantity(x.item, x.quantity * crafts) for x in recipe.inputs), market, observations)
    fees = recipe.fees if craft_fees is None else craft_fees
    issues = ['missing_material_prices'] if materials.missing else []
    if fees is None:
        issues.append('unknown_crafting_fees')
    fee_total = 0
    for fee in fees or ():
        require(fee.money.currency == market.currency, 'CURRENCY_MISMATCH', 'Craft fee currency differs')
        multiplier = sum(x.quantity for x in recipe.outcomes[0].outputs) * crafts if fee.basis is FeeBasis.OUTPUT_UNIT else crafts
        fee_total += units(fee.money.amount, market) * multiplier
    cost = None if materials.total is None or fees is None else materials.total + fee_total
    fixed = units(sale_fees.fixed, market)
    retention = 1 - Fraction(sale_fees.tax_rate)
    if selling_price is None:
        issues.append('missing_selling_price')
    proceeds = None if selling_price is None else rounded(target.quantity * units(selling_price, market) * retention, sale_fees.rounding) - fixed
    profit = None if proceeds is None or cost is None else proceeds - cost
    roi = None if profit is None or cost == 0 else Fraction(profit * 100, cost)
    if cost == 0:
        issues.append('roi_undefined_zero_cost')
    denominator = target.quantity * retention
    be = None if cost is None or denominator == 0 else Fraction(cost + fixed, 1) / denominator
    if denominator == 0:
        issues.append('break_even_undefined_full_tax')
    # Smallest integer-unit price whose rounded net proceeds cover cost.
    minimum = None
    if be is not None:
        low, high = 0, rounded(be, 'ceil')
        while low < high:
            mid = (low + high) // 2
            if rounded(mid * denominator, sale_fees.rounding) >= cost + fixed:
                high = mid
            else:
                low = mid + 1
        minimum = low
    if len(recipe.outcomes[0].outputs) > 1:
        issues.append('coproducts_unvalued')
    return EconomicsResult(crafts, produced, target.quantity, produced - target.quantity, materials,
                           cost, proceeds, profit, roi, be, minimum, tuple(issues))
