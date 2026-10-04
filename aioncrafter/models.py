"""Version-1 catalog, observation and calculation records; exact JSON amounts."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import re

from .codec import require, validate_fields
from .identity import (CatalogScope, Currency, DatasetKind, ItemIdentity, MarketScope,
                       PriceIdentity, Tradability, identifier, normalize_alias)


def exact(value: str, label: str) -> Decimal:
    require(type(value) is str and len(value) <= 100 and re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value) is not None,
            "AMOUNT", f"{label} must be a nonnegative plain decimal string")
    return Decimal(value)


def timestamp(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        require(False, "TIMESTAMP", "Timestamp must be ISO 8601")
    require(result.tzinfo is not None and result.utcoffset() is not None, "TIMESTAMP", "Timezone is required")
    return result


class RightsStatus(str, Enum):
    SYNTHETIC = "synthetic"
    PERMITTED = "permitted"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class Provenance:
    source_id: str
    source_ref: str
    dataset_kind: DatasetKind
    rights_status: RightsStatus
    rights_ref: str

    def __post_init__(self):
        validate_fields(self)
        for name in ("source_id", "source_ref", "rights_ref"):
            identifier(getattr(self, name), name)
        require((self.dataset_kind is DatasetKind.SYNTHETIC) == (self.rights_status is RightsStatus.SYNTHETIC),
                "PROVENANCE", "Synthetic origin must be explicitly labeled in rights status")


@dataclass(frozen=True)
class Money:
    amount: str
    currency: Currency

    def __post_init__(self):
        validate_fields(self)
        value = exact(self.amount.removeprefix("-"), "amount")
        require(-value.as_tuple().exponent <= self.currency.decimal_places, "PRECISION", "Amount exceeds currency precision")

    @property
    def decimal(self) -> Decimal:
        return Decimal(self.amount)


@dataclass(frozen=True)
class Alias:
    language: str
    text: str

    def __post_init__(self):
        validate_fields(self)
        require(re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*", self.language) is not None,
                "LANGUAGE", "Use a language tag, e.g. en, es, zh-TW")
        identifier(self.text, "alias")


class AcquisitionKind(str, Enum):
    AUCTION = "auction"
    VENDOR = "vendor_purchase"
    CRAFT = "craft"
    OTHER = "other"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Acquisition:
    kind: AcquisitionKind
    currency: Currency | None
    quantity_limit: int | None
    restrictions: tuple[str, ...]

    def __post_init__(self):
        validate_fields(self)
        require(self.quantity_limit is None or self.quantity_limit >= 0, "QUANTITY", "Acquisition limit must be nonnegative or unknown")
        for value in self.restrictions:
            identifier(value, "restriction")


@dataclass(frozen=True)
class Item:
    identity: ItemIdentity
    aliases: tuple[Alias, ...]
    acquisition: tuple[Acquisition, ...]

    def __post_init__(self):
        validate_fields(self)
        require(bool(self.aliases), "ALIAS", "At least one display/search alias is required")
        aliases = [(a.language.casefold(), normalize_alias(a.text)) for a in self.aliases]
        require(len(set(aliases)) == len(aliases), "DUPLICATE_ALIAS", "Duplicate aliases within item")
        if any(a.kind is AcquisitionKind.AUCTION for a in self.acquisition):
            require(self.identity.variant.tradability is Tradability.TRADEABLE, "TRADABILITY", "Auction acquisition requires a tradeable variant")


@dataclass(frozen=True)
class ItemQuantity:
    item: ItemIdentity
    quantity: int

    def __post_init__(self):
        validate_fields(self)
        require(self.quantity > 0, "QUANTITY", "Item quantity must be a positive integer")


@dataclass(frozen=True)
class Outcome:
    outputs: tuple[ItemQuantity, ...]
    probability: str | None
    probability_source: str | None

    def __post_init__(self):
        validate_fields(self)
        require(len({x.item.key for x in self.outputs}) == len(self.outputs), "DUPLICATE_OUTPUT", "Combine repeated outputs in an outcome")
        if self.probability is not None:
            require(exact(self.probability, "probability") <= 1, "PROBABILITY", "Probability must lie in [0,1]")
            require(self.probability_source is not None, "PROBABILITY_SOURCE", "Known probabilities require evidence")
        if self.probability_source is not None:
            identifier(self.probability_source, "probability source")


class FeeBasis(str, Enum):
    ATTEMPT = "per_attempt"
    BATCH = "per_batch"
    OUTPUT_UNIT = "per_output_unit"


@dataclass(frozen=True)
class CraftFee:
    money: Money
    basis: FeeBasis

    def __post_init__(self):
        validate_fields(self)
        require(self.money.decimal >= 0, "AMOUNT", "Craft fees must be nonnegative")


@dataclass(frozen=True)
class Recipe:
    recipe_id: str
    scope: CatalogScope
    inputs: tuple[ItemQuantity, ...]
    outcomes: tuple[Outcome, ...]
    fees: tuple[CraftFee, ...] | None
    requirements: tuple[str, ...] | None
    provenance: Provenance

    def __post_init__(self):
        validate_fields(self)
        identifier(self.recipe_id, "recipe_id")
        require(bool(self.inputs) and bool(self.outcomes), "RECIPE", "Recipe needs inputs and outcomes")
        require(any(o.outputs for o in self.outcomes), "RECIPE", "At least one outcome must produce an item")
        require(len({x.item.key for x in self.inputs}) == len(self.inputs), "DUPLICATE_INPUT", "Combine repeated inputs")
        # Integer scaling avoids Decimal context rounding for large exact strings.
        known = [Decimal(o.probability) for o in self.outcomes if o.probability is not None]
        scale = max([-p.as_tuple().exponent for p in known] + [0])
        total = sum(int("".join(str(d) for d in p.as_tuple().digits)) * 10 ** (scale + p.as_tuple().exponent) for p in known)
        require(total <= 10 ** scale, "PROBABILITY", "Known probabilities exceed 1")
        if len(known) == len(self.outcomes):
            require(total == 10 ** scale, "PROBABILITY", "Exhaustive outcomes must sum exactly to 1")
        require(self.scope.dataset_kind is self.provenance.dataset_kind, "PROVENANCE", "Recipe source must match dataset kind")
        if self.requirements is not None:
            for value in self.requirements:
                identifier(value, "requirement")


@dataclass(frozen=True)
class Catalog:
    schema_version: int
    release_id: str
    scope: CatalogScope
    provenance: Provenance
    items: tuple[Item, ...]
    recipes: tuple[Recipe, ...]

    def __post_init__(self):
        validate_fields(self)
        require(self.schema_version == 1, "SCHEMA_VERSION", "Supported catalog schema is 1")
        identifier(self.release_id, "release_id")


class PriceType(str, Enum):
    MANUAL = "manual_observation"
    VENDOR_PURCHASE = "vendor_purchase"
    VENDOR_SELL_BACK = "vendor_sell_back"
    LISTING = "listing"
    MINIMUM_LISTING = "minimum_listing"
    SNAPSHOT = "aggregate_snapshot"
    COMPLETED_SALE = "completed_sale"


@dataclass(frozen=True)
class PriceObservation:
    schema_version: int
    observation_id: str
    identity: PriceIdentity
    price_type: PriceType
    unit_price: str | None
    available_quantity: int | None
    observed_at: str | None
    fetched_at: str
    provenance: Provenance
    supersedes_id: str | None

    def __post_init__(self):
        validate_fields(self)
        require(self.schema_version == 1, "SCHEMA_VERSION", "Supported observation schema is 1")
        identifier(self.observation_id, "observation_id")
        if self.supersedes_id is not None:
            identifier(self.supersedes_id, "supersedes_id")
            require(self.supersedes_id != self.observation_id, "OVERRIDE", "An observation cannot replace itself")
        if self.unit_price is not None:
            require(Money(self.unit_price, self.identity.market.currency).decimal >= 0, "AMOUNT", "Prices must be nonnegative")
        require(self.available_quantity is None or self.available_quantity >= 0, "QUANTITY", "Available stock must be nonnegative or unknown")
        fetched = timestamp(self.fetched_at)
        if self.observed_at is not None:
            require(timestamp(self.observed_at) <= fetched, "TIMESTAMP", "Observation cannot be later than ingestion")
        require(self.identity.item.scope.dataset_kind is self.provenance.dataset_kind, "PROVENANCE", "Observation origin must match item/market kind")
        if self.price_type in (PriceType.LISTING, PriceType.MINIMUM_LISTING, PriceType.SNAPSHOT, PriceType.COMPLETED_SALE):
            require(self.identity.item.variant.tradability is Tradability.TRADEABLE, "TRADABILITY", "Market observations require a tradeable variant")

    @property
    def acquisition_reference(self) -> bool:
        return self.price_type not in (PriceType.VENDOR_SELL_BACK, PriceType.COMPLETED_SALE)


class Completeness(str, Enum):
    UNKNOWN = "unknown"
    PARTIAL = "partial"
    COMPLETE = "complete"


@dataclass(frozen=True)
class NamedAmount:
    name: str
    money: Money | None

    def __post_init__(self):
        validate_fields(self)
        identifier(self.name, "result name")


@dataclass(frozen=True)
class Calculation:
    schema_version: int
    calculation_id: str
    catalog_release_id: str
    market: MarketScope
    inputs: tuple[ItemQuantity, ...]
    recipe_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    assumptions: tuple[str, ...]
    results: tuple[NamedAmount, ...]
    completeness: Completeness
    created_at: str

    def __post_init__(self):
        validate_fields(self)
        require(self.schema_version == 1, "SCHEMA_VERSION", "Supported calculation schema is 1")
        identifier(self.calculation_id, "calculation_id")
        identifier(self.catalog_release_id, "catalog release")
        timestamp(self.created_at)
        require(self.market.resolved, "UNRESOLVED_SCOPE", "Saved calculations require a market")
        require(bool(self.inputs), "CALCULATION", "At least one requested item is required")
        for entry in self.inputs:
            PriceIdentity(entry.item, self.market)
        for group in (self.recipe_ids, self.observation_ids, self.assumptions):
            for value in group:
                identifier(value, "calculation reference/assumption")
        require(len({x.name for x in self.results}) == len(self.results), "CALCULATION", "Result names must be unique")
        for result in self.results:
            if result.money is not None:
                require(result.money.currency == self.market.currency, "CURRENCY_MISMATCH", "Result currency differs from calculation market")
        if self.completeness is Completeness.COMPLETE:
            require(bool(self.results) and all(x.money is not None for x in self.results), "COMPLETENESS", "Complete calculations cannot contain unknown results")
