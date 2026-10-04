"""One-attempt scenarios; exact expectations, never guaranteed recursive yields."""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from .codec import require, validate_fields
from .economics import MaterialsResult, SaleFees, materials_cost, rounded, units
from .identity import ItemIdentity, MarketScope, PriceIdentity, Tradability, identifier
from .models import (CraftFee, FeeBasis, ItemQuantity, Money, PriceObservation, Recipe,
                     RightsStatus, exact)


@dataclass(frozen=True)
class BonusOutput:
    """A Bernoulli bonus on every attempt, separate from exclusive recipe outcomes.

    Correlated/conditional bonuses must instead be encoded as exhaustive joint
    recipe outcomes. A source string is an assertion to audit, not verification by us.
    """
    bonus_id: str
    outputs: tuple[ItemQuantity, ...]
    probability: str | None
    probability_source: str | None

    def __post_init__(self):
        validate_fields(self)
        identifier(self.bonus_id, 'bonus ID')
        require(bool(self.outputs) and len({q.item for q in self.outputs}) == len(self.outputs),
                'BONUS', 'A bonus needs distinct positive outputs')
        if self.probability is not None:
            require(exact(self.probability, 'bonus probability') <= 1, 'PROBABILITY', 'Bonus probability exceeds one')
            require(self.probability_source is not None, 'PROBABILITY_SOURCE', 'Known bonus probability requires a source')
        if self.probability_source is not None:
            identifier(self.probability_source, 'bonus probability source')


@dataclass(frozen=True)
class AttemptEvidence:
    # Bind attestations to exact content, including build/probabilities/fees, so they
    # cannot silently migrate to an updated recipe or bonus definition.
    recipe: Recipe
    bonuses: tuple[BonusOutput, ...]
    probabilities_ref: str | None
    full_consumption_ref: str | None
    independent_bonuses_ref: str | None

    def __post_init__(self):
        validate_fields(self)
        for ref in (self.probabilities_ref, self.full_consumption_ref, self.independent_bonuses_ref):
            if ref is not None:
                identifier(ref, 'attempt evidence')


@dataclass(frozen=True)
class PlannedSale:
    item: ItemIdentity
    quantity_limit: int
    unit_price: Money | None
    fees: SaleFees | None

    def __post_init__(self):
        validate_fields(self)
        require(self.quantity_limit >= 0, 'QUANTITY', 'Planned sale limit must be nonnegative')
        if self.unit_price is not None:
            require(self.unit_price.decimal >= 0, 'AMOUNT', 'Selling price must be nonnegative')
        require(self.quantity_limit == 0 or self.item.variant.tradability is Tradability.TRADEABLE,
                'TRADABILITY', 'Bound/unknown variants cannot be planned market sales')


@dataclass(frozen=True)
class AttemptScenario:
    outcome_index: int
    bonuses: tuple[str, ...]
    probability: Fraction | None
    outputs: tuple[ItemQuantity, ...]
    sold: tuple[ItemQuantity, ...]
    leftovers: tuple[ItemQuantity, ...]
    revenue: int | None
    crafting_fees: int | None
    cost: int | None
    profit: int | None


@dataclass(frozen=True)
class StochasticResult:
    recipe: Recipe
    evidence: AttemptEvidence
    materials: MaterialsResult
    scenarios: tuple[AttemptScenario, ...]
    expected_revenue: Fraction | None
    expected_cost: Fraction | None
    expected_profit: Fraction | None
    worst_profit: int | None
    best_profit: int | None
    loss_probability: Fraction | None
    issues: tuple[str, ...]


def attempt_economics(recipe: Recipe, market: MarketScope, references: tuple[PriceObservation, ...],
                      sales: tuple[PlannedSale, ...], *, evidence: AttemptEvidence,
                      bonuses: tuple[BonusOutput, ...] = (),
                      fee_override: tuple[CraftFee, ...] | None = None,
                      max_scenarios: int) -> StochasticResult:
    """Enumerate one attempt with full-input consumption only when attested.

    All outputs in one recipe outcome occur together. Outcomes are mutually exclusive.
    Bonus events are separate Bernoulli events, independent of the outcome and one
    another only when explicitly attested. Fees are rounded per item sale/scenario
    before weighting expectations. Unplanned outputs receive no resale credit.
    This cannot infer source truth, sale probability, repeated-attempt independence,
    refunds or partial consumption. Unsupported rules remain unknown.
    """
    require(type(recipe) is Recipe and type(market) is MarketScope and market.resolved, 'TYPE', 'Expected recipe and explicit market')
    require(type(bonuses) is tuple and all(type(b) is BonusOutput for b in bonuses), 'TYPE', 'Expected bonus tuple')
    require(len({b.bonus_id for b in bonuses}) == len(bonuses), 'BONUS', 'Bonus IDs must be distinct')
    require(type(evidence) is AttemptEvidence and evidence.recipe == recipe and evidence.bonuses == bonuses,
            'EVIDENCE_SCOPE', 'Evidence must bind this exact recipe/build and bonuses')
    require(type(max_scenarios) is int and max_scenarios > 0
            and len(bonuses) < max_scenarios.bit_length()
            and len(recipe.outcomes) * 2 ** len(bonuses) <= max_scenarios,
            'SEARCH_LIMIT', 'Scenarios exceed the explicit work budget')
    require(recipe.provenance.rights_status is not RightsStatus.UNVERIFIED, 'RIGHTS', 'Recipe rights are unverified')
    require(type(sales) is tuple and all(type(s) is PlannedSale for s in sales), 'TYPE', 'Expected planned sales')
    require(len({s.item for s in sales}) == len(sales), 'DUPLICATE_SALE', 'Combine sales by variant')
    outputs = {q.item for o in recipe.outcomes for q in o.outputs} | {q.item for b in bonuses for q in b.outputs}
    for item in outputs | {q.item for q in recipe.inputs}:
        require(item.scope == recipe.scope, 'SCOPE_MISMATCH', 'Recipe or bonus item/build differs')
        PriceIdentity(item, market)
    for sale in sales:
        require(sale.item in outputs, 'OUTPUT', 'Planned sale must be a modeled output')
        if sale.unit_price is not None:
            require(sale.unit_price.currency == market.currency, 'CURRENCY_MISMATCH', 'Selling currency differs')
        if sale.fees is not None:
            units(sale.fees.fixed, market)
    fees = recipe.fees if fee_override is None else fee_override
    require(fees is None or (type(fees) is tuple and all(type(f) is CraftFee for f in fees)), 'TYPE', 'Expected crafting fees')
    for fee in fees or ():
        require(fee.money.currency == market.currency, 'CURRENCY_MISMATCH', 'Crafting currency differs')
    require(type(references) is tuple and all(type(o) is PriceObservation for o in references), 'TYPE', 'Expected references')
    require(all(o.provenance.rights_status is not RightsStatus.UNVERIFIED for o in references), 'RIGHTS', 'Reference rights are unverified')
    materials = materials_cost(recipe.inputs, market, references)
    issues = ['one_attempt_only', 'sale_quantities_assumed_not_guaranteed', 'stock_unverified', 'leftovers_without_resale_credit']
    if materials.total is None:
        issues.append('missing_material_prices')
    if evidence.full_consumption_ref is None:
        issues.append('unknown_failure_consumption')
    if evidence.probabilities_ref is None:
        issues.append('unverified_probabilities')
    if bonuses and evidence.independent_bonuses_ref is None:
        issues.append('unverified_bonus_independence')
    if any(o.probability is None for o in recipe.outcomes) or any(b.probability is None for b in bonuses):
        issues.append('unknown_probabilities')
    if fees is None:
        issues.append('unknown_crafting_fees')
    if recipe.requirements is None:
        issues.append('unknown_requirements')
    elif recipe.requirements:
        issues.append('confirm_requirements')
    probabilities_usable = evidence.probabilities_ref is not None and (not bonuses or evidence.independent_bonuses_ref is not None)
    scenarios = []
    for index, outcome in enumerate(recipe.outcomes):
        for flags in product((False, True), repeat=len(bonuses)):
            factors = [None if outcome.probability is None else Fraction(outcome.probability)]
            quantities = {q.item: q.quantity for q in outcome.outputs}
            for bonus, occurs in zip(bonuses, flags):
                p = None if bonus.probability is None else Fraction(bonus.probability)
                factors.append(p if occurs or p is None else 1 - p)
                if occurs:
                    for q in bonus.outputs:
                        quantities[q.item] = quantities.get(q.item, 0) + q.quantity
            # Zero probability is usable only after the evidence/independence gate.
            probability = None
            if probabilities_usable:
                if any(p == 0 for p in factors):
                    probability = Fraction(0)
                elif all(p is not None for p in factors):
                    probability = Fraction(1)
                    for p in factors:
                        probability *= p
            made = tuple(ItemQuantity(i, n) for i, n in sorted(quantities.items(), key=lambda x: x[0].key))
            leftovers, sold = dict(quantities), []
            revenue, unknown_revenue = 0, False
            for sale in sales:
                quantity = min(quantities.get(sale.item, 0), sale.quantity_limit)
                if not quantity:
                    continue
                sold.append(ItemQuantity(sale.item, quantity))
                leftovers[sale.item] -= quantity
                if sale.unit_price is None or sale.fees is None:
                    unknown_revenue = True
                    issues.append('missing_sale_price_or_fees')
                else:
                    revenue += rounded(quantity * units(sale.unit_price.amount, market) * (1 - Fraction(sale.fees.tax_rate)),
                                       sale.fees.rounding) - units(sale.fees.fixed, market)
            fee_total = None if fees is None else sum(units(f.money.amount, market) *
                         (sum(quantities.values()) if f.basis is FeeBasis.OUTPUT_UNIT else 1) for f in fees)
            cost = None if materials.total is None or fee_total is None or evidence.full_consumption_ref is None else materials.total + fee_total
            net = None if unknown_revenue else revenue
            scenarios.append(AttemptScenario(index, tuple(b.bonus_id for b, flag in zip(bonuses, flags) if flag),
                             probability, made, tuple(sold), tuple(ItemQuantity(i, n) for i, n in sorted(leftovers.items(), key=lambda x: x[0].key) if n),
                             net, fee_total, cost, None if cost is None or net is None else net - cost))
    possible = [s for s in scenarios if s.probability != 0]
    def expected(field):
        if any(s.probability is None or getattr(s, field) is None for s in possible):
            return None
        return sum((s.probability * getattr(s, field) for s in possible), Fraction(0))
    complete_profit = all(s.profit is not None for s in possible)
    return StochasticResult(recipe, evidence, materials, tuple(scenarios), expected('revenue'), expected('cost'), expected('profit'),
                            min(s.profit for s in possible) if complete_profit else None,
                            max(s.profit for s in possible) if complete_profit else None,
                            sum((s.probability for s in possible if s.profit < 0), Fraction(0))
                            if complete_profit and all(s.probability is not None for s in possible) else None,
                            tuple(sorted(set(issues))))
