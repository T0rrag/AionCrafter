"""Exact acquisition from a supplied listing snapshot, never a live-stock promise."""
from dataclasses import dataclass

from .codec import require, validate_fields
from .economics import units
from .identity import PriceIdentity
from .models import PriceObservation, PriceType, RightsStatus
from .providers import PriceCapabilities


@dataclass(frozen=True)
class ListingOffer:
    observation: PriceObservation
    total_price: str
    partial_purchase: bool

    def __post_init__(self):
        validate_fields(self)
        obs = self.observation
        require(obs.price_type is PriceType.LISTING, 'PRICE_TYPE', 'Depth requires listing observations')
        require(obs.available_quantity is not None and obs.available_quantity > 0,
                'QUANTITY', 'Offer must declare a positive number of units')
        total = units(self.total_price, obs.identity.market)
        if obs.unit_price is not None:
            require(total == units(obs.unit_price, obs.identity.market) * obs.available_quantity,
                    'STACK_PRICE', 'Unit and whole-offer prices disagree')
        require(not self.partial_purchase or obs.unit_price is not None,
                'STACK_PRICE', 'Partial purchases require an exact unit price')


@dataclass(frozen=True)
class Purchase:
    observation_id: str
    quantity: int
    cost: int  # Integer currency units.


@dataclass(frozen=True)
class AcquisitionResult:
    identity: PriceIdentity
    requested: int
    purchased: int
    missing: int
    leftovers: int
    known_cost: int
    total: int | None
    state: str
    stock: str
    purchases: tuple[Purchase, ...]
    observations: tuple[PriceObservation, ...]


def _request(identity, quantity):
    require(type(identity) is PriceIdentity, 'TYPE', 'Expected PriceIdentity')
    require(type(quantity) is int and quantity > 0, 'QUANTITY', 'Requested quantity must be positive')


def indicative_cost(identity: PriceIdentity, quantity: int,
                    reference: PriceObservation | None) -> AcquisitionResult:
    """Minimum/reference multiplication is an estimate; it never proves stock."""
    _request(identity, quantity)
    if reference is not None:
        require(type(reference) is PriceObservation and reference.identity == identity,
                'SCOPE_MISMATCH', 'Reference differs from requested identity')
        require(reference.acquisition_reference, 'PRICE_TYPE', 'Sale history/sell-back cannot price acquisition')
        require(reference.provenance.rights_status is not RightsStatus.UNVERIFIED,
                'RIGHTS', 'Reference rights are unverified')
    total = None if reference is None or reference.unit_price is None else quantity * units(reference.unit_price, identity.market)
    return AcquisitionResult(identity, quantity, 0, quantity, 0, 0, total,
                             'unavailable' if total is None else 'indicative', 'unverified', (),
                             () if reference is None else (reference,))


def depth_cost(identity: PriceIdentity, quantity: int, offers: tuple[ListingOffer, ...],
               capabilities: PriceCapabilities, *, max_states: int) -> AcquisitionResult:
    """Minimum cash cost for supplied offers; whole stacks are indivisible.

    Sparse exact subset search handles whole stacks, followed by cheapest divisible
    units for each subset. max_states is a caller-selected computational work budget
    (cumulative candidates), not a provider limit. Exceeding it fails explicitly; no
    heuristic is silently presented as an optimum. No leftover resale credit.
    """
    _request(identity, quantity)
    require(type(offers) is tuple and all(type(o) is ListingOffer for o in offers), 'TYPE', 'Expected offer tuple')
    require(type(max_states) is int and max_states > 0, 'LIMIT', 'Supply a positive search budget')
    require(type(capabilities) is PriceCapabilities and capabilities.listing_depth and identity.market in capabilities.scopes,
            'CAPABILITIES', 'Provider must explicitly support listing depth and this market')
    seen = set()
    for offer in offers:
        obs = offer.observation
        require(obs.identity == identity, 'SCOPE_MISMATCH', 'Offer differs from requested identity')
        require(obs.observation_id not in seen, 'DUPLICATE_ID', 'An offer cannot be counted twice')
        seen.add(obs.observation_id)
        require(obs.provenance.rights_status is not RightsStatus.UNVERIFIED, 'RIGHTS', 'Offer rights unverified')
        # This contract accepts one homogeneous acquisition snapshot, not history.
        require(obs.provenance == offers[0].observation.provenance and obs.fetched_at == offers[0].observation.fetched_at,
                'SNAPSHOT', 'Do not mix provider sources or ingestion snapshots')
    available = sum(o.observation.available_quantity for o in offers)
    observations = tuple(o.observation for o in offers)
    if available < quantity:
        purchases = tuple(Purchase(o.observation.observation_id, o.observation.available_quantity,
                                   units(o.total_price, identity.market)) for o in offers)
        return AcquisitionResult(identity, quantity, available, quantity - available, 0,
                                 sum(p.cost for p in purchases), None, 'insufficient', 'snapshot_only', purchases, observations)
    whole = sorted((o for o in offers if not o.partial_purchase), key=lambda o: o.observation.observation_id)
    partial = sorted((o for o in offers if o.partial_purchase),
                     key=lambda o: (units(o.observation.unit_price, identity.market), o.observation.observation_id))
    # Capped quantity -> (cost, actual quantity, purchases). Once covered, buying
    # another nonnegative-cost stack cannot improve cost or leftovers.
    states = {0: (0, 0, ())}
    work = 0
    for offer in whole:
        obs = offer.observation
        price = units(offer.total_price, identity.market)
        next_states = dict(states)
        for covered, (cost, purchased, selected) in states.items():
            if covered == quantity:
                continue
            work += 1
            require(work <= max_states, 'SEARCH_LIMIT', 'Whole-stack search exceeded the explicit work budget')
            new_qty = purchased + obs.available_quantity
            key = min(quantity, new_qty)
            candidate = (cost + price, new_qty, selected + (Purchase(obs.observation_id, obs.available_quantity, price),))
            prior = next_states.get(key)
            if prior is None or candidate[:2] < prior[:2]:
                next_states[key] = candidate
        states = next_states
    best = None
    for cost, purchased, selected in states.values():
        for offer in partial:
            if purchased >= quantity:
                break
            work += 1
            require(work <= max_states, 'SEARCH_LIMIT', 'Listing search exceeded the explicit work budget')
            obs = offer.observation
            take = min(quantity - purchased, obs.available_quantity)
            subtotal = take * units(obs.unit_price, identity.market)
            purchased += take
            cost += subtotal
            selected += (Purchase(obs.observation_id, take, subtotal),)
        if purchased >= quantity and (best is None or (cost, purchased) < best[:2]):
            best = (cost, purchased, selected)
    require(best is not None, 'COVERAGE', 'No supported purchase combination covers demand')
    cost, purchased, selected = best
    return AcquisitionResult(identity, quantity, purchased, 0, purchased - quantity, cost, cost,
                             'covered', 'snapshot_only', selected, observations)
