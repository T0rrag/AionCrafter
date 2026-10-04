"""Typed market evidence; no inference of sell-through from asking prices."""
from dataclasses import dataclass
from datetime import datetime, timedelta

from .codec import require, validate_fields
from .identity import PriceIdentity, Tradability, identifier
from .models import PriceObservation, PriceType, Provenance, RightsStatus, timestamp
from .price_cache import duration


def freshness(observed_at: str | None, fetched_at: str, *, now: datetime, max_age: timedelta) -> str:
    require(type(now) is datetime and now.tzinfo is not None and now.utcoffset() is not None,
            'CLOCK', 'A timezone-aware evaluation time is required')
    duration(max_age, 'max_age')
    if timestamp(fetched_at) > now:
        return 'future'
    if observed_at is None:
        return 'unknown'
    age = now - timestamp(observed_at)
    return 'future' if age < timedelta(0) else 'stale' if age > max_age else 'fresh'


@dataclass(frozen=True)
class SalesVolume:
    """Explicit provider-reported completed units in a closed interval.

    Preserve samples separately: overlapping windows/sources are never summed.
    available_quantity on a price observation is not a sales-volume field.
    """
    evidence_id: str
    identity: PriceIdentity
    sold_units: int | None
    window_start: str
    window_end: str
    observed_at: str | None
    fetched_at: str
    provenance: Provenance

    def __post_init__(self):
        validate_fields(self)
        identifier(self.evidence_id, 'volume evidence ID')
        require(self.sold_units is None or self.sold_units >= 0, 'QUANTITY', 'Sales volume must be nonnegative or unknown')
        require(self.identity.item.variant.tradability is Tradability.TRADEABLE, 'TRADABILITY', 'Market sales need a tradeable variant')
        start, end, fetched = timestamp(self.window_start), timestamp(self.window_end), timestamp(self.fetched_at)
        require(start < end <= fetched, 'TIMESTAMP', 'Volume interval must close by ingestion')
        if self.observed_at is not None:
            require(end <= timestamp(self.observed_at) <= fetched, 'TIMESTAMP', 'Volume observation must follow its interval')
        require(self.provenance.dataset_kind == self.identity.item.scope.dataset_kind, 'PROVENANCE', 'Volume dataset differs')


@dataclass(frozen=True)
class LiquidityEvidence:
    identity: PriceIdentity
    asking_prices: tuple[PriceObservation, ...]
    completed_sales: tuple[PriceObservation, ...]
    other_references: tuple[PriceObservation, ...]
    volumes: tuple[SalesVolume, ...]
    # Parallel to all observations, then volumes, in supplied order.
    freshness: tuple[str, ...]
    issues: tuple[str, ...]


def liquidity_evidence(identity: PriceIdentity, observations: tuple[PriceObservation, ...],
                       volumes: tuple[SalesVolume, ...], *, now: datetime, max_age: timedelta) -> LiquidityEvidence:
    require(type(identity) is PriceIdentity, 'TYPE', 'Expected market identity')
    require(type(observations) is tuple and all(type(o) is PriceObservation for o in observations), 'TYPE', 'Expected observations')
    require(type(volumes) is tuple and all(type(v) is SalesVolume for v in volumes), 'TYPE', 'Expected volume records')
    require(len({o.observation_id for o in observations}) == len(observations), 'DUPLICATE_ID', 'Observation IDs repeat')
    require(len({v.evidence_id for v in volumes}) == len(volumes), 'DUPLICATE_ID', 'Volume IDs repeat')
    states = []
    for record in (*observations, *volumes):
        require(record.identity == identity, 'SCOPE_MISMATCH', 'Market/build/variant evidence differs')
        require(record.provenance.rights_status is not RightsStatus.UNVERIFIED, 'RIGHTS', 'Market evidence rights unverified')
        states.append(freshness(record.observed_at, record.fetched_at, now=now, max_age=max_age))
    # Validate clock/policy even for an empty evidence set.
    require(type(now) is datetime and now.tzinfo is not None and now.utcoffset() is not None, 'CLOCK', 'Expected aware time')
    duration(max_age, 'max_age')
    asking = tuple(o for o in observations if o.price_type in (PriceType.LISTING, PriceType.MINIMUM_LISTING))
    completed = tuple(o for o in observations if o.price_type is PriceType.COMPLETED_SALE)
    other = tuple(o for o in observations if o not in asking and o not in completed)
    issues = ['sell_through_unknown', 'asking_prices_are_not_completed_sales']
    if not any(v.sold_units is not None for v in volumes):
        issues.append('sales_volume_unknown')
    if not any(o.available_quantity is not None for o in asking):
        issues.append('listing_stock_unknown')
    if any(state != 'fresh' for state in states):
        issues.append('stale_or_unknown_evidence')
    return LiquidityEvidence(identity, asking, completed, other, volumes, tuple(states), tuple(issues))


def quantity_label(observation: PriceObservation) -> str:
    """Label stock without misreading the legacy available_quantity field as sales."""
    if observation.price_type is PriceType.COMPLETED_SALE:
        return 'Completed-sale price; sales volume requires separate interval evidence. Sell-through unknown.'
    quantity = 'unknown' if observation.available_quantity is None else str(observation.available_quantity)
    if observation.price_type in (PriceType.LISTING, PriceType.MINIMUM_LISTING):
        return f'Asking price; reported listing stock: {quantity}. Snapshot only; sell-through unknown.'
    if observation.price_type is PriceType.VENDOR_PURCHASE:
        return f'Reported vendor stock: {quantity}. Vendor restrictions need confirmation; market sales volume unknown.'
    return f'Reported reference quantity: {quantity}. Meaning/coverage require source confirmation; market sales volume unknown.'
