"""Quantity-aware cost comparison for explicit deterministic craft/buy routes."""
from dataclasses import dataclass
from itertools import combinations

from .acquisition import AcquisitionResult, ListingOffer, depth_cost, indicative_cost
from .batches import BatchPlan, plan_batches
from .codec import ValidationError, require, validate_fields
from .economics import units
from .identity import MarketScope, PriceIdentity
from .models import Catalog, CraftFee, FeeBasis, ItemQuantity, PriceObservation
from .providers import PriceCapabilities
from .valuation import InventoryEntry


@dataclass(frozen=True)
class ListingBook:
    identity: PriceIdentity
    offers: tuple[ListingOffer, ...]
    capabilities: PriceCapabilities

    def __post_init__(self):
        validate_fields(self)


@dataclass(frozen=True)
class PlanCost:
    plan: BatchPlan
    acquisitions: tuple[AcquisitionResult, ...]
    materials_total: int | None
    known_materials: int
    crafting_fees: int | None
    known_fees: int
    total: int | None
    issues: tuple[str, ...]


def price_plan(plan: BatchPlan, market: MarketScope, references: tuple[PriceObservation, ...], *,
               books: tuple[ListingBook, ...] = (), fee_overrides: dict[str, tuple[CraftFee, ...] | None] | None = None,
               max_states: int = 10000) -> PlanCost:
    """Cost external acquisition plus all executed craft fees, in currency units.

    Owned inputs were already consumed by the plan. For replacement valuation, build
    the plan without inventory. A reference quote is always indicative/stock unverified.
    A supplied book prices actual required quantity within that snapshot only.
    """
    require(type(plan) is BatchPlan and type(market) is MarketScope and market.resolved, 'TYPE', 'Expected a plan and explicit market')
    require(type(references) is tuple and all(type(x) is PriceObservation for x in references), 'TYPE', 'Expected reference tuple')
    require(type(books) is tuple and all(type(x) is ListingBook for x in books), 'TYPE', 'Expected listing books')
    require(type(max_states) is int and max_states > 0, 'SEARCH_LIMIT', 'Supply a positive acquisition budget')
    sources = {}
    for source in (*references, *books):
        require(source.identity.market == market, 'SCOPE_MISMATCH', 'Source market differs from plan')
        require(source.identity.item not in sources, 'DUPLICATE_PRICE', 'Select one reference or book per variant')
        sources[source.identity.item] = source
    for line in plan.lines:
        PriceIdentity(line.item, market)
    overrides = {} if fee_overrides is None else fee_overrides
    require(type(overrides) is dict, 'TYPE', 'Expected fee override mapping')
    require(set(overrides) <= {s.recipe.recipe_id for s in plan.steps}, 'UNUSED_FEE', 'Override belongs to an unexecuted recipe')
    for fees in overrides.values():
        require(fees is None or (type(fees) is tuple and all(type(f) is CraftFee for f in fees)), 'TYPE', 'Expected explicit fees or unknown')
    costs, issues = [], list(plan.issues)
    for material in plan.materials:
        identity = PriceIdentity(material.item, market)
        source = sources.get(material.item)
        if isinstance(source, ListingBook):
            result = depth_cost(identity, material.quantity, source.offers, source.capabilities, max_states=max_states)
            issues.append('stock_snapshot_only')
        else:
            result = indicative_cost(identity, material.quantity, source)
            issues.append('stock_unverified')
        if result.total is None:
            issues.append('incomplete_acquisition')
        costs.append(result)
    known_materials = sum(x.total if x.total is not None else x.known_cost for x in costs)
    materials_total = None if any(x.total is None for x in costs) else known_materials
    known_fees, missing_fee = 0, False
    for step in plan.steps:
        fees = overrides.get(step.recipe.recipe_id, step.recipe.fees)
        if fees is None:
            missing_fee = True
            issues.append(f'unknown_crafting_fees:{step.recipe.recipe_id}')
            continue
        for fee in fees:
            require(fee.money.currency == market.currency, 'CURRENCY_MISMATCH', 'Craft fee currency differs')
            multiplier = sum(q.quantity for q in step.outputs) if fee.basis is FeeBasis.OUTPUT_UNIT else step.crafts
            known_fees += units(fee.money.amount, market) * multiplier
    fee_total = None if missing_fee else known_fees
    total = None if materials_total is None or missing_fee else materials_total + known_fees
    if any(line.owned_used for line in plan.lines):
        issues.append('owned_inputs_excluded_from_cash')
    if plan.leftovers:
        issues.append('leftovers_without_resale_credit')
    return PlanCost(plan, tuple(costs), materials_total, known_materials, fee_total, known_fees, total,
                    tuple(sorted(set(issues))))


@dataclass(frozen=True)
class RouteCost:
    selected_recipes: tuple[str, ...]
    cost: PlanCost


@dataclass(frozen=True)
class RouteComparison:
    objective: str
    routes: tuple[RouteCost, ...]
    lowest_known: tuple[RouteCost, ...]
    unresolved_routes: int
    scope: str = 'all-or-nothing recipe subsets; no mixed purchase/craft of the same variant'


def compare_routes(catalog: Catalog, requested: tuple[ItemQuantity, ...], candidate_recipes: tuple[str, ...],
                   market: MarketScope, references: tuple[PriceObservation, ...], *, objective: str,
                   inventory: tuple[InventoryEntry, ...] = (), books: tuple[ListingBook, ...] = (),
                   fee_overrides: dict[str, tuple[CraftFee, ...] | None] | None = None,
                   max_routes: int, max_states: int = 10000) -> RouteComparison:
    """Enumerate a bounded strategy family, not a globally optimal general solver.

    'additional_cash' uses supplied inventory; 'replacement_cost' ignores owned stock.
    No route mixes buying and crafting units of the same item or runs competing producers.
    Costs preserve unknowns and source evidence. lowest_known is a conditional numerical
    comparison, not a recommendation, proof of available stock, or a realized profit.
    """
    require(objective in ('additional_cash', 'replacement_cost'), 'OBJECTIVE', 'Choose a cost objective explicitly')
    require(type(candidate_recipes) is tuple and all(type(r) is str for r in candidate_recipes)
            and len(set(candidate_recipes)) == len(candidate_recipes), 'RECIPE', 'Choose distinct candidate recipe IDs')
    require(type(max_routes) is int and max_routes > 0 and len(candidate_recipes) < max_routes.bit_length(),
            'SEARCH_LIMIT', 'Recipe subsets exceed the explicit route budget')
    plan_batches(catalog, requested, (), inventory=inventory)
    # Validate all candidate contracts, even if an all-buy route could avoid them.
    # Competing recipes are permitted as alternatives, not simultaneous producers.
    for recipe_id in candidate_recipes:
        plan_batches(catalog, requested, (recipe_id,), inventory=inventory)
    overrides = {} if fee_overrides is None else fee_overrides
    require(type(overrides) is dict and set(overrides) <= set(candidate_recipes), 'UNUSED_FEE', 'Fee overrides must belong to candidates')
    for fees in overrides.values():
        require(fees is None or (type(fees) is tuple and all(type(f) is CraftFee for f in fees)), 'TYPE', 'Expected explicit fees or unknown')
        for fee in fees or ():
            require(fee.money.currency == market.currency, 'CURRENCY_MISMATCH', 'Craft fee currency differs')
    routes = []
    for count in range(len(candidate_recipes) + 1):
        for selected in combinations(sorted(candidate_recipes), count):
            try:
                plan = plan_batches(catalog, requested, selected,
                                    inventory=inventory if objective == 'additional_cash' else ())
            except ValidationError as exc:
                if exc.code == 'AMBIGUOUS_PRODUCER':
                    continue
                raise
            used = {s.recipe.recipe_id for s in plan.steps}
            cost = price_plan(plan, market, references, books=books,
                              fee_overrides={r: f for r, f in overrides.items() if r in used}, max_states=max_states)
            routes.append(RouteCost(selected, cost))
    known = [r for r in routes if r.cost.total is not None]
    best = min((r.cost.total for r in known), default=None)
    return RouteComparison(objective, tuple(routes), tuple(r for r in known if r.cost.total == best),
                           sum(r.cost.total is None for r in routes))
