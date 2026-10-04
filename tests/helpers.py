from pathlib import Path

from aioncrafter.catalog import import_catalog
from aioncrafter.identity import Currency, DatasetKind, FactionMode, MarketKind, MarketScope, PriceIdentity
from aioncrafter.models import Calculation, Completeness, ItemQuantity, NamedAmount, PriceObservation, PriceType

FIXTURE = Path(__file__).parent / "fixtures/SYNTHETIC-catalog-v1.json"


def catalog():
    return import_catalog(FIXTURE.read_bytes())


def market():
    return MarketScope(DatasetKind.SYNTHETIC, "SYNTHETIC", MarketKind.SERVER, "test-server",
                       FactionMode.NOT_APPLICABLE, None, Currency("synthetic-demo", "TEST", 2))


def observation():
    c = catalog()
    return PriceObservation(1, "obs-1", PriceIdentity(c.items[0].identity, market()), PriceType.MANUAL,
                            "12.30", None, None, "2026-10-04T10:00:00Z", c.provenance, None)


def calculation():
    c = catalog()
    return Calculation(1, "calc-1", c.release_id, market(), (ItemQuantity(c.items[0].identity, 3),), (),
                       ("obs-1",), ("SYNTHETIC: storage test only; no economics engine",),
                       (NamedAmount("total", None),), Completeness.UNKNOWN, "2026-10-04T11:00:00Z")
