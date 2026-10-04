"""Stable identities: exact source IDs, explicitly scoped; aliases never form keys."""
from dataclasses import dataclass
from enum import Enum
import unicodedata

from .codec import dumps, require, validate_fields


def identifier(value: str, name: str) -> None:
    require(type(value) is str and 0 < len(value) <= 256 and value == value.strip()
            and all(not unicodedata.category(c).startswith("C") for c in value),
            "IDENTIFIER", f"{name} must be nonempty, trimmed text without control characters")


class DatasetKind(str, Enum):
    SYNTHETIC = "SYNTHETIC"
    GAME = "GAME"


class Tradability(str, Enum):
    TRADEABLE = "tradeable"
    BOUND = "bound"
    UNKNOWN = "unknown"


class FactionMode(str, Enum):
    SPECIFIC = "specific"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class MarketKind(str, Enum):
    SERVER = "server"
    GROUP = "group"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CatalogScope:
    namespace: str
    region: str
    build: str
    dataset_kind: DatasetKind

    def __post_init__(self):
        validate_fields(self)
        for name in ("namespace", "region", "build"):
            identifier(getattr(self, name), name)


@dataclass(frozen=True)
class Variant:
    quality: str | None
    enhancement: int | None
    tradability: Tradability
    attributes: tuple[tuple[str, str], ...]

    def __post_init__(self):
        validate_fields(self)
        if self.quality is not None:
            identifier(self.quality, "quality")
        require(self.enhancement is None or self.enhancement >= 0, "VARIANT", "Enhancement must be nonnegative or unknown")
        for name, value in self.attributes:
            identifier(name, "attribute name")
            identifier(value, "attribute value")
        require(len({k for k, _ in self.attributes}) == len(self.attributes), "DUPLICATE_ATTRIBUTE", "Variant attributes repeat")
        object.__setattr__(self, "attributes", tuple(sorted(self.attributes)))

    @property
    def resolved(self) -> bool:
        return self.quality is not None and self.enhancement is not None and self.tradability is not Tradability.UNKNOWN


@dataclass(frozen=True)
class ItemIdentity:
    scope: CatalogScope
    item_id: str
    variant: Variant

    def __post_init__(self):
        validate_fields(self)
        identifier(self.item_id, "item_id")

    @property
    def key(self) -> str:
        return "item:v1:" + dumps(self)


@dataclass(frozen=True)
class Currency:
    namespace: str
    code: str
    decimal_places: int

    def __post_init__(self):
        validate_fields(self)
        identifier(self.namespace, "currency namespace")
        identifier(self.code, "currency code")
        require(0 <= self.decimal_places <= 18, "CURRENCY", "Precision must be 0..18")


@dataclass(frozen=True)
class MarketScope:
    dataset_kind: DatasetKind
    region: str | None
    kind: MarketKind
    market_id: str | None
    faction_mode: FactionMode
    faction_id: str | None
    currency: Currency | None

    def __post_init__(self):
        validate_fields(self)
        for name in ("region", "market_id", "faction_id"):
            if getattr(self, name) is not None:
                identifier(getattr(self, name), name)
        require((self.faction_mode is FactionMode.SPECIFIC) == (self.faction_id is not None),
                "FACTION", "Only a specific faction has a faction_id")
        require((self.kind is MarketKind.UNKNOWN) == (self.market_id is None),
                "MARKET", "Known market kinds require an ID; unknown markets have no ID")

    @property
    def resolved(self) -> bool:
        return self.region is not None and self.kind is not MarketKind.UNKNOWN and self.currency is not None and self.faction_mode is not FactionMode.UNKNOWN


@dataclass(frozen=True)
class PriceIdentity:
    item: ItemIdentity
    market: MarketScope

    def __post_init__(self):
        validate_fields(self)
        require(self.item.variant.resolved and self.market.resolved, "UNRESOLVED_SCOPE", "Price identity needs a complete variant and market")
        require(self.item.scope.region == self.market.region and self.item.scope.dataset_kind is self.market.dataset_kind,
                "SCOPE_MISMATCH", "Item and market region/dataset must match")

    @property
    def key(self) -> str:
        return "price:v1:" + dumps(self)


def normalize_alias(text: str) -> str:
    """Search normalization only: accent/case/spacing insensitive, not identity."""
    identifier(text, "alias")
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return " ".join("".join(c for c in decomposed if not unicodedata.combining(c)).split())
