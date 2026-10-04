"""Source-aware manual observations and explicit material-list resolution."""
from datetime import datetime, timezone
from uuid import uuid4
from .catalog import CatalogIndex
from .codec import require
from .identity import PriceIdentity
from .models import ItemQuantity, PriceObservation, PriceType


def manual_observation(item, market, price, observed_at, provenance, *, now=None):
    require(bool(observed_at), 'TIMESTAMP', 'Manual prices require observation time')
    return PriceObservation(1, str(uuid4()), PriceIdentity(item, market), PriceType.MANUAL,
                            price if price != '' else None, None, observed_at,
                            now or datetime.now(timezone.utc).isoformat(), provenance, None)


def resolve_list(catalog, text, language='en'):
    """Lines are quantity<TAB>exact alias. Return candidates; never pick a variant."""
    index = CatalogIndex(catalog)
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        quantity, separator, name = line.partition('\t')
        require(bool(separator) and quantity.isascii() and quantity.isdigit() and int(quantity) > 0,
                'MATERIAL_LIST', 'Use positive quantity, TAB, exact item name per line')
        candidates = index.search(name.strip(), language, catalog.scope)
        require(bool(candidates), 'ITEM_NOT_FOUND', name)
        rows.append((int(quantity), candidates))
    require(bool(rows), 'MATERIAL_LIST', 'List is empty')
    return tuple(rows)
