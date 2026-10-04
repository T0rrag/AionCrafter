"""Contracts only. No automatic, vendor or manual-entry adapter is connected."""
from dataclasses import dataclass
from typing import Protocol

from .codec import require, validate_fields
from .identity import MarketScope, PriceIdentity, identifier
from .models import Catalog, PriceObservation


@dataclass(frozen=True)
class PriceCapabilities:
    provider_id: str
    scopes: tuple[MarketScope, ...]
    listing_depth: bool
    completed_sales: bool
    source_timestamps: bool
    update_behavior: str
    rights_reference: str

    def __post_init__(self):
        validate_fields(self)
        for name in ("provider_id", "update_behavior", "rights_reference"):
            identifier(getattr(self, name), name)
        require(all(s.resolved for s in self.scopes), "UNRESOLVED_SCOPE", "Claimed provider scopes must be explicit")


class CatalogProvider(Protocol):
    def get_catalog(self, release_id: str) -> Catalog: ...


class PriceProvider(Protocol):
    @property
    def capabilities(self) -> PriceCapabilities: ...

    def observations_for(self, identity: PriceIdentity) -> tuple[PriceObservation, ...]:
        """Return observations for this exact identity; empty tuple means missing."""
        ...


class BatchPriceProvider(PriceProvider, Protocol):
    def observations_for_batch(self, identities: tuple[PriceIdentity, ...]) -> dict[PriceIdentity, tuple[PriceObservation, ...]]:
        """Explicit opt-in batching; return every requested key (empty means missing)."""
        ...
