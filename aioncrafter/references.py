"""Offline, user-supplied reference imports; no provider access or rights inference."""
from datetime import datetime, timezone
from .codec import loads, require
from .identity import PriceIdentity
from .models import PriceObservation, PriceType, RightsStatus, timestamp
from .liquidity import quantity_label


SUPPORTED = (PriceType.MANUAL, PriceType.VENDOR_PURCHASE, PriceType.SNAPSHOT)


def validate_references(observations, catalog, market):
    require(bool(observations), 'REFERENCE_EMPTY', 'Supply at least one observation')
    known = {PriceIdentity(item.identity, market) for item in catalog.items}
    require(len({o.identity for o in observations}) == len(observations), 'DUPLICATE_PRICE', 'One reference per variant')
    require(len({o.observation_id for o in observations}) == len(observations), 'REFERENCE_ID', 'Observation IDs repeat')
    for obs in observations:
        require(obs.identity in known, 'REFERENCE_SCOPE', 'Reference must match catalog variant and selected market/currency')
        require(obs.price_type in SUPPORTED, 'REFERENCE_TYPE', 'Use manual, vendor purchase or aggregate snapshot')
        require(obs.provenance.rights_status in (RightsStatus.SYNTHETIC, RightsStatus.PERMITTED),
                'REFERENCE_RIGHTS', 'A permitted source and rights reference are required')
        require(obs.price_type is not PriceType.MANUAL or obs.observed_at is not None,
                'TIMESTAMP', 'Manual observations require an observation time')
    return observations


def import_references(text, catalog, market):
    require(type(text) is str and len(text.encode('utf-8')) <= 262144, 'REFERENCE_SIZE', 'References exceed 256 KiB')
    return validate_references(loads(tuple[PriceObservation, ...], text), catalog, market)


def merge_references(previous, imported, catalog, market):
    """Preview atomically; replaying an ID may never change its displayed record."""
    validate_references(previous, catalog, market)
    validate_references(imported, catalog, market)
    by_id = {obs.observation_id: obs for obs in previous}
    for obs in imported:
        require(obs.observation_id not in by_id or obs == by_id[obs.observation_id],
                'REFERENCE_ID', 'An existing observation ID cannot change; supply a new ID')
    merged = {obs.identity: obs for obs in previous}
    merged.update({obs.identity: obs for obs in imported})
    return validate_references(tuple(merged.values()), catalog, market)


def reference_label(obs, *, now=None):
    if obs is None:
        return 'Unavailable · age unknown'
    title = {PriceType.MANUAL: 'Manual', PriceType.VENDOR_PURCHASE: 'Vendor purchase',
             PriceType.SNAPSHOT: 'Snapshot'}.get(obs.price_type, obs.price_type.value)
    state = ' · unavailable' if obs.unit_price is None else ''
    if obs.observed_at is None:
        age = 'age unknown'
    else:
        seconds = ((now or datetime.now(timezone.utc)) - timestamp(obs.observed_at)).total_seconds()
        age = 'future observation — check clock' if seconds < 0 else f'age {int(seconds) // 3600}h {(int(seconds) % 3600) // 60}m'
    return f'{title}{state} · {age} · observed {obs.observed_at or "unknown"} · ingested {obs.fetched_at} · source {obs.provenance.source_id} ({obs.provenance.source_ref}) · rights {obs.provenance.rights_status.value}: {obs.provenance.rights_ref} · {quantity_label(obs)}'
