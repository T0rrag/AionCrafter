"""Conditional ranking of explicit deterministic craft plans, with exclusion reasons."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from fractions import Fraction

from .batches import plan_batches
from .buycraft import ListingBook, PlanCost, price_plan
from .catalog import validate_catalog
from .codec import require, validate_fields
from .economics import SaleFees, rounded, units
from .identity import MarketScope, PriceIdentity, Tradability, identifier
from .liquidity import LiquidityEvidence, SalesVolume, freshness, liquidity_evidence
from .models import AcquisitionKind, Catalog, CraftFee, ItemQuantity, Money, PriceObservation, PriceType, RightsStatus
from .valuation import InventoryEntry


@dataclass(frozen=True)
class RecipeAccess:
    recipe_id: str
    profession: str | None
    profession_ref: str | None
    confirmed_requirements: tuple[str, ...]

    def __post_init__(self):
        validate_fields(self)
        identifier(self.recipe_id, 'recipe ID')
        for value in (self.profession, self.profession_ref, *self.confirmed_requirements):
            if value is not None:
                identifier(value, 'recipe eligibility evidence')


@dataclass(frozen=True)
class RankingPolicy:
    budget: Money
    professions: tuple[str, ...]
    access: tuple[RecipeAccess, ...]
    confirmed_vendor_restrictions: tuple[str, ...]
    max_source_age_seconds: int
    sort_by: str

    def __post_init__(self):
        validate_fields(self)
        require(self.budget.decimal >= 0, 'BUDGET', 'Budget must be nonnegative')
        require(0 <= self.max_source_age_seconds <= timedelta.max.days * 86400 + timedelta.max.seconds,
                'DURATION', 'Source age limit must be a representable nonnegative duration')
        require(self.sort_by in ('profit', 'roi', 'capital'), 'SORT', 'Choose profit, roi or capital')
        require(len({a.recipe_id for a in self.access}) == len(self.access), 'DUPLICATE_RECIPE', 'Access records repeat')
        for value in (*self.professions, *self.confirmed_vendor_restrictions):
            identifier(value, 'ranking filter')


@dataclass(frozen=True)
class CraftCandidate:
    candidate_id: str
    target: ItemQuantity
    recipe_ids: tuple[str, ...]
    selling_reference: PriceObservation | None
    sale_fees: SaleFees | None

    def __post_init__(self):
        validate_fields(self)
        identifier(self.candidate_id, 'candidate ID')


@dataclass(frozen=True)
class RankedCraft:
    candidate: CraftCandidate
    replacement: PlanCost
    cash: PlanCost
    profit: int | None
    capital_required: int | None
    roi_percent: Fraction | None
    observations: tuple[PriceObservation, ...]
    freshness: tuple[str, ...]
    liquidity: LiquidityEvidence
    excluded_reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class CraftRanking:
    ranked: tuple[RankedCraft, ...]
    excluded: tuple[RankedCraft, ...]
    scope: str = 'Conditional estimates for supplied deterministic routes; no sell-through guarantee or general optimization'


def rank_crafts(catalog: Catalog, candidates: tuple[CraftCandidate, ...], market: MarketScope,
                references: tuple[PriceObservation, ...], *, policy: RankingPolicy, now: datetime,
                inventory: tuple[InventoryEntry, ...] = (), books: tuple[ListingBook, ...] = (),
                volumes: tuple[SalesVolume, ...] = (), max_candidates: int, max_states: int = 10000,
                fee_overrides: dict[str, tuple[CraftFee, ...] | None] | None = None) -> CraftRanking:
    """Rank complete current estimates, keeping excluded results visible with reasons.

    Profit/ROI charge replacement cost; budget uses additional cash plus fixed sale
    fees. Explicit recipe/profession attestations and vendor restrictions are checked,
    never inferred from recipe IDs or translated names. All source times are preserved.
    Listing/ref estimates remain conditional even when they pass these filters.
    """
    require(type(catalog) is Catalog and type(market) is MarketScope and market.resolved, 'TYPE', 'Expected catalog and market')
    validate_catalog(catalog)
    require(type(policy) is RankingPolicy and policy.budget.currency == market.currency, 'CURRENCY_MISMATCH', 'Ranking budget currency differs')
    require(type(candidates) is tuple and all(type(c) is CraftCandidate for c in candidates), 'TYPE', 'Expected candidates')
    require(type(max_candidates) is int and max_candidates > 0 and len(candidates) <= max_candidates, 'SEARCH_LIMIT', 'Candidate budget exceeded')
    require(len({c.candidate_id for c in candidates}) == len(candidates), 'DUPLICATE_ID', 'Candidate IDs repeat')
    require(type(volumes) is tuple and all(type(v) is SalesVolume for v in volumes), 'TYPE', 'Expected volume tuple')
    require(all(v.identity.market == market for v in volumes), 'SCOPE_MISMATCH', 'Volume market differs')
    max_age = timedelta(seconds=policy.max_source_age_seconds)
    # Empty input must still validate clock and freshness policy.
    require(type(now) is datetime and now.tzinfo is not None and now.utcoffset() is not None, 'CLOCK', 'Expected aware evaluation time')
    items = {i.identity: i for i in catalog.items}
    access = {a.recipe_id: a for a in policy.access}
    require(set(access) <= {r.recipe_id for r in catalog.recipes}, 'RECIPE', 'Eligibility evidence belongs to another catalog')
    overrides = {} if fee_overrides is None else fee_overrides
    require(type(overrides) is dict and set(overrides) <= {r.recipe_id for r in catalog.recipes}, 'UNUSED_FEE', 'Override belongs to another catalog')
    for fees in overrides.values():
        require(fees is None or (type(fees) is tuple and all(type(f) is CraftFee for f in fees)), 'TYPE', 'Expected crafting fees')
        require(all(f.money.currency == market.currency for f in fees or ()), 'CURRENCY_MISMATCH', 'Craft fee currency differs')
    def price(plan):
        used = {s.recipe.recipe_id for s in plan.steps}
        return price_plan(plan, market, references, books=books, max_states=max_states,
                          fee_overrides={r: f for r, f in overrides.items() if r in used})
    ranked, excluded = [], []
    for candidate in candidates:
        identity = PriceIdentity(candidate.target.item, market)
        replacement_plan = plan_batches(catalog, (candidate.target,), candidate.recipe_ids)
        cash_plan = plan_batches(catalog, (candidate.target,), candidate.recipe_ids, inventory=inventory)
        replacement = price(replacement_plan)
        cash = price(cash_plan)
        reasons, warnings = [], ['sell_through_unknown', 'conditional_price_estimate']
        if not cash_plan.steps:
            reasons.append('no_crafting_required')
        if candidate.target.item.variant.tradability is not Tradability.TRADEABLE:
            reasons.append('output_not_tradeable')
        for recipe in {s.recipe.recipe_id: s.recipe for s in (*replacement_plan.steps, *cash_plan.steps)}.values():
            a = access.get(recipe.recipe_id)
            if a is None or a.profession is None or a.profession_ref is None:
                reasons.append('unknown_profession:' + recipe.recipe_id)
            elif a.profession not in policy.professions:
                reasons.append('profession_filtered:' + recipe.recipe_id)
            if recipe.requirements is None:
                reasons.append('unknown_requirements:' + recipe.recipe_id)
            elif a is None or not set(recipe.requirements) <= set(a.confirmed_requirements):
                reasons.append('unconfirmed_requirements:' + recipe.recipe_id)
        observations = {}
        for cost in (replacement, cash):
            warnings.extend(i for i in cost.issues if i in ('stock_unverified', 'stock_snapshot_only', 'leftovers_without_resale_credit'))
            for acquisition in cost.acquisitions:
                for obs in acquisition.observations:
                    prior = observations.get(obs.observation_id)
                    require(prior is None or prior == obs, 'IMMUTABLE_ID', 'Observation ID changed across cost views')
                    observations[obs.observation_id] = obs
                # Check eligibility for both accounting views: an impossible external
                # replacement purchase must not create a credible profit estimate.
                item = items[acquisition.identity.item]
                vendor = next((o for o in acquisition.observations if o.price_type is PriceType.VENDOR_PURCHASE), None)
                if acquisition.state == 'indicative' and any(o.available_quantity is not None and o.available_quantity < acquisition.requested
                                                            for o in acquisition.observations):
                    reasons.append('insufficient_reported_quantity:' + item.identity.item_id)
                if item.identity.variant.tradability is not Tradability.TRADEABLE and vendor is None:
                    reasons.append('bound_or_unknown_external_input:' + item.identity.item_id)
                if vendor is not None:
                    channels = [a for a in item.acquisition if a.kind is AcquisitionKind.VENDOR and a.currency == market.currency]
                    eligible = [a for a in channels if set(a.restrictions) <= set(policy.confirmed_vendor_restrictions)
                                and (a.quantity_limit is None or a.quantity_limit >= acquisition.requested)]
                    if not eligible:
                        reasons.append('vendor_eligibility_unconfirmed:' + item.identity.item_id)
                    if any(a.quantity_limit is None for a in eligible):
                        warnings.append('vendor_limit_unknown')
                    if vendor.available_quantity is not None and vendor.available_quantity < acquisition.requested:
                        reasons.append('insufficient_vendor_stock:' + item.identity.item_id)
        sale = candidate.selling_reference
        if sale is not None:
            require(sale.identity == identity, 'SCOPE_MISMATCH', 'Selling reference differs from target variant/market/build')
            require(sale.price_type not in (PriceType.VENDOR_PURCHASE, PriceType.VENDOR_SELL_BACK), 'PRICE_TYPE', 'Market sale estimate needs a market/manual reference')
            require(sale.provenance.rights_status is not RightsStatus.UNVERIFIED, 'RIGHTS', 'Selling reference rights unverified')
            prior = observations.get(sale.observation_id)
            require(prior is None or prior == sale, 'IMMUTABLE_ID', 'Selling observation ID changed')
            observations[sale.observation_id] = sale
        used = tuple(observations.values())
        states = tuple(freshness(o.observed_at, o.fetched_at, now=now, max_age=max_age) for o in used)
        if any(state != 'fresh' for state in states):
            reasons.append('stale_future_or_unknown_price_age')
        profit = capital = roi = None
        if replacement.total is None or cash.total is None or sale is None or sale.unit_price is None or candidate.sale_fees is None:
            reasons.append('incomplete_prices_or_fees')
        else:
            fees = candidate.sale_fees
            fixed = units(fees.fixed, market)
            revenue = rounded(candidate.target.quantity * units(sale.unit_price, market) * (1 - Fraction(fees.tax_rate)), fees.rounding) - fixed
            profit = revenue - replacement.total
            capital = cash.total + fixed
            roi = None if replacement.total == 0 else Fraction(profit * 100, replacement.total)
            if capital > units(policy.budget.amount, market):
                reasons.append('over_budget')
            if profit <= 0:
                reasons.append('nonpositive_profit')
            if roi is None:
                warnings.append('roi_undefined_zero_cost')
                if policy.sort_by == 'roi':
                    reasons.append('undefined_roi')
        liquidity = liquidity_evidence(identity, () if sale is None else (sale,), tuple(v for v in volumes if v.identity == identity),
                                       now=now, max_age=max_age)
        warnings.extend(liquidity.issues)
        result = RankedCraft(candidate, replacement, cash, profit, capital, roi, used, states, liquidity,
                             tuple(sorted(set(reasons))), tuple(sorted(set(warnings))))
        (excluded if reasons else ranked).append(result)
    def key(result):
        metric = result.profit if policy.sort_by == 'profit' else result.roi_percent if policy.sort_by == 'roi' else -result.capital_required
        return (-metric, result.candidate.candidate_id)
    return CraftRanking(tuple(sorted(ranked, key=key)), tuple(excluded))
