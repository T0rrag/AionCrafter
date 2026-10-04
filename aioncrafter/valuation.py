"""Inventory and recorded material costs, separate from replacement valuation."""
from dataclasses import dataclass

from .codec import require, validate_fields
from .economics import MaterialsResult, units
from .identity import ItemIdentity, MarketScope, PriceIdentity, identifier
from .models import Money


@dataclass(frozen=True)
class InventoryEntry:
    item: ItemIdentity
    quantity: int

    def __post_init__(self):
        validate_fields(self)
        require(self.quantity >= 0, 'QUANTITY', 'Owned quantity must be nonnegative')


@dataclass(frozen=True)
class HistoricalCost:
    """Actual recorded cost allocated to consumed units in this plan, not stock value."""
    identity: PriceIdentity
    quantity: int
    total_cost: Money
    reference: str

    def __post_init__(self):
        validate_fields(self)
        require(self.quantity > 0, 'QUANTITY', 'Recorded consumed quantity must be positive')
        require(self.total_cost.currency == self.identity.market.currency,
                'CURRENCY_MISMATCH', 'Recorded cost must use the plan currency')
        require(self.total_cost.decimal >= 0, 'AMOUNT', 'Recorded cost must be nonnegative')
        identifier(self.reference, 'historical cost reference')


@dataclass(frozen=True)
class ValuationLine:
    item: ItemIdentity
    required: int
    owned_used: int
    to_buy: int
    replacement_cost: int | None
    additional_cash: int | None
    recorded_cost: int | None


@dataclass(frozen=True)
class ValuationResult:
    lines: tuple[ValuationLine, ...]
    replacement_total: int | None
    additional_cash: int | None
    cash_known_subtotal: int
    recorded_total: int | None
    recorded_known_subtotal: int
    missing_cash_prices: tuple[str, ...]
    missing_records: tuple[str, ...]


def value_materials(materials: MaterialsResult, market: MarketScope,
                    inventory: tuple[InventoryEntry, ...] = (),
                    history: tuple[HistoricalCost, ...] = ()) -> ValuationResult:
    """Consume inventory once after demand aggregation; partial ledgers stay unknown.

    Historical entries must be explicit allocations to this plan's consumed inputs.
    Exactly covering a line makes its recorded cost known. Over-allocation is refused;
    no FIFO/LIFO, average-cost, resale-value or missing-zero assumption is introduced.
    """
    owned = {}
    for entry in inventory:
        PriceIdentity(entry.item, market)
        require(entry.item.key not in owned, 'DUPLICATE_INVENTORY', 'Combine owned quantities per variant')
        owned[entry.item.key] = entry.quantity
    required = {line.item.item.key: line.item.quantity for line in materials.lines}
    records = {}
    for record in history:
        require(record.identity.market == market, 'SCOPE_MISMATCH', 'Recorded cost market differs')
        key = record.identity.item.key
        require(key in required, 'UNUSED_RECORD', 'Historical allocation must belong to a required material')
        quantity, cost = records.get(key, (0, 0))
        records[key] = (quantity + record.quantity, cost + units(record.total_cost.amount, market))
        require(records[key][0] <= required[key], 'HISTORY_OVERALLOCATION', 'Recorded quantity exceeds consumed demand')
    lines, missing_cash, missing_history = [], [], []
    for material in materials.lines:
        key, quantity = material.item.item.key, material.item.quantity
        used = min(owned.get(key, 0), quantity)
        buy = quantity - used
        observation = material.observation
        if buy == 0:
            cash = 0
        elif observation is None or observation.unit_price is None:
            cash = None
            missing_cash.append(key)
        else:
            cash = units(observation.unit_price, market) * buy
        recorded_quantity, recorded_cost = records.get(key, (0, 0))
        if recorded_quantity != quantity:
            recorded_cost = None
            missing_history.append(key)
        lines.append(ValuationLine(material.item.item, quantity, used, buy, material.subtotal, cash, recorded_cost))
    cash_known = sum(line.additional_cash for line in lines if line.additional_cash is not None)
    history_known = sum(line.recorded_cost for line in lines if line.recorded_cost is not None)
    return ValuationResult(tuple(lines), materials.total, None if missing_cash else cash_known, cash_known,
                           None if missing_history else history_known, history_known,
                           tuple(missing_cash), tuple(missing_history))
