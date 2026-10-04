"""Optional append-only actual records with explicit FIFO basis; no estimated prices."""
from dataclasses import dataclass
from fractions import Fraction
import sqlite3

from .codec import dumps, loads, require, validate_fields
from .economics import units
from .identity import ItemIdentity, MarketScope, Tradability, identifier
from .models import Catalog, ItemQuantity, Money, exact, timestamp
from .plans import catalog_digest


@dataclass(frozen=True)
class RecordSource:
    record_id: str
    occurred_at: str
    reference: str

    def __post_init__(self):
        validate_fields(self)
        identifier(self.record_id, 'record ID')
        identifier(self.reference, 'actual record reference')
        timestamp(self.occurred_at)


@dataclass(frozen=True)
class StockRecord:
    source: RecordSource
    kind: str
    acquired: ItemQuantity
    total_paid: Money | None

    def __post_init__(self):
        validate_fields(self)
        require(self.kind in ('opening', 'purchase'), 'LEDGER_KIND', 'Choose opening stock or purchase')
        require(self.total_paid is None or self.total_paid.decimal >= 0, 'AMOUNT', 'Actual cost must be nonnegative or unknown')


@dataclass(frozen=True)
class OutputShare:
    item: ItemIdentity
    fraction: str

    def __post_init__(self):
        validate_fields(self)
        require(exact(self.fraction, 'cost share') <= 1, 'ALLOCATION', 'Cost share must lie in [0,1]')


@dataclass(frozen=True)
class CraftRecord:
    source: RecordSource
    consumed: tuple[ItemQuantity, ...]
    produced: tuple[ItemQuantity, ...]
    fee_paid: Money | None
    output_shares: tuple[OutputShare, ...] | None

    def __post_init__(self):
        validate_fields(self)
        require(bool(self.consumed), 'QUANTITY', 'Record actual consumed inputs, even for a failed craft')
        for entries in (self.consumed, self.produced):
            require(len({q.item for q in entries}) == len(entries), 'DUPLICATE_ITEM', 'Combine actual quantities by variant')
        require(self.fee_paid is None or self.fee_paid.decimal >= 0, 'AMOUNT', 'Fee must be nonnegative or unknown')
        if self.output_shares is not None:
            require(len({s.item for s in self.output_shares}) == len(self.output_shares)
                    and {s.item for s in self.output_shares} == {q.item for q in self.produced},
                    'ALLOCATION', 'Shares must cover each actual output exactly once')
            require(sum((Fraction(s.fraction) for s in self.output_shares), Fraction(0)) == (1 if self.produced else 0),
                    'ALLOCATION', 'Output shares must sum exactly to one, or be empty for failure')


@dataclass(frozen=True)
class SaleRecord:
    source: RecordSource
    sold: ItemQuantity
    gross_received: Money | None
    fees_paid: Money | None

    def __post_init__(self):
        validate_fields(self)
        require(self.sold.item.variant.tradability is Tradability.TRADEABLE, 'TRADABILITY', 'Market sales require a tradeable variant')
        for amount in (self.gross_received, self.fees_paid):
            require(amount is None or amount.decimal >= 0, 'AMOUNT', 'Actual proceeds/fees must be nonnegative or unknown')


@dataclass(frozen=True)
class Journal:
    schema_version: int
    name: str
    catalog_digest: str
    market: MarketScope
    cost_method: str
    records: tuple[StockRecord | CraftRecord | SaleRecord, ...]
    estimated_profit: Money | None = None

    def __post_init__(self):
        validate_fields(self)
        require(self.schema_version == 1, 'LEDGER_VERSION', 'Supported ledger schema is 1')
        identifier(self.name, 'journal name')
        require(self.cost_method == 'fifo', 'COST_METHOD', 'This ledger requires explicit FIFO cost attribution')
        require(self.market.resolved, 'UNRESOLVED_SCOPE', 'Select an explicit journal market')
        require(len(self.records) <= 1000, 'LEDGER_SIZE', 'A journal is limited to 1000 actual records')


@dataclass(frozen=True)
class StockBalance:
    item: ItemIdentity
    quantity: int
    historical_basis: Fraction | None


@dataclass(frozen=True)
class LedgerResult:
    inventory: tuple[StockBalance, ...]
    realized_profit: Fraction | None
    known_realized_subtotal: Fraction
    net_cash_flow: int | None
    known_cash_subtotal: int
    recorded_estimate: Fraction | None
    realized_less_estimate: Fraction | None
    issues: tuple[str, ...]


def evaluate_journal(journal: Journal, catalog: Catalog) -> LedgerResult:
    require(type(journal) is Journal and type(catalog) is Catalog, 'TYPE', 'Expected journal and catalog')
    require(journal.catalog_digest == catalog_digest(catalog), 'LEDGER_CATALOG', 'Journal belongs to different catalog content')
    require(journal.market.region == catalog.scope.region and journal.market.dataset_kind == catalog.scope.dataset_kind,
            'SCOPE_MISMATCH', 'Journal market differs from catalog')
    estimate = None
    if journal.estimated_profit is not None:
        require(journal.estimated_profit.currency == journal.market.currency, 'CURRENCY_MISMATCH', 'Recorded estimate currency differs')
        estimate = Fraction(journal.estimated_profit.amount) * 10 ** journal.market.currency.decimal_places
    items = {i.identity for i in catalog.items}
    lots, seen, issues = {}, set(), set()
    known_profit, known_cash = Fraction(0), 0
    unknown_profit = unknown_cash = activity = False
    previous_time = None
    def paid(value):
        if value is None:
            return None
        require(value.currency == journal.market.currency, 'CURRENCY_MISMATCH', 'Actual amount currency differs')
        return units(value.amount, journal.market)
    def check(item):
        require(item in items, 'ORPHAN_ITEM', 'Actual record variant/build is outside catalog')
    def put(entry, basis):
        check(entry.item)
        lots.setdefault(entry.item, []).append([entry.quantity, basis])
    def consume(entry):
        check(entry.item)
        queue = lots.get(entry.item, [])
        require(sum(q for q, _ in queue) >= entry.quantity, 'INSUFFICIENT_STOCK', 'Actual consumption exceeds recorded stock')
        remaining, basis, missing = entry.quantity, Fraction(0), False
        while remaining:
            quantity, total = queue[0]
            take = min(remaining, quantity)
            portion = None if total is None else total * Fraction(take, quantity)
            if portion is None:
                missing = True
            else:
                basis += portion
            remaining -= take
            if take == quantity:
                queue.pop(0)
            else:
                queue[0] = [quantity - take, None if total is None else total - portion]
        return None if missing else basis
    for record in journal.records:
        source = record.source
        require(source.record_id not in seen, 'DUPLICATE_ID', 'Actual record IDs repeat')
        seen.add(source.record_id)
        occurred = timestamp(source.occurred_at)
        require(previous_time is None or occurred >= previous_time, 'LEDGER_ORDER', 'Records must be chronological; listed order breaks timestamp ties')
        previous_time = occurred
        if type(record) is StockRecord:
            total = paid(record.total_paid)
            if record.kind == 'opening':
                require(not activity, 'LEDGER_ORDER', 'Opening stock must precede purchases, crafts and sales')
            else:
                activity = True
                if total is None:
                    unknown_cash = True
                else:
                    known_cash -= total
            put(record.acquired, None if total is None else Fraction(total))
        elif type(record) is CraftRecord:
            activity = True
            costs = tuple(consume(q) for q in record.consumed)
            fee = paid(record.fee_paid)
            if fee is None:
                unknown_cash = True
            else:
                known_cash -= fee
            cost = None if fee is None or any(c is None for c in costs) else sum(costs, Fraction(fee))
            if not record.produced:
                if cost is None:
                    unknown_profit = True
                else:
                    known_profit -= cost
                issues.add('failed_craft_cost_expensed')
            else:
                shares = ({s.item: Fraction(s.fraction) for s in record.output_shares} if record.output_shares is not None
                          else {record.produced[0].item: Fraction(1)} if len(record.produced) == 1 else {})
                if not shares:
                    issues.add('multi_output_basis_unallocated')
                for q in record.produced:
                    put(q, None if cost is None or q.item not in shares else cost * shares[q.item])
        else:
            activity = True
            basis = consume(record.sold)
            gross, fee = paid(record.gross_received), paid(record.fees_paid)
            if gross is None or fee is None:
                unknown_cash = True
            known_cash += (gross or 0) - (fee or 0)
            if basis is None or gross is None or fee is None:
                unknown_profit = True
            else:
                known_profit += gross - fee - basis
    balances = tuple(StockBalance(item, sum(q for q, _ in queue),
                                 None if any(b is None for _, b in queue) else sum((b for _, b in queue), Fraction(0)))
                     for item, queue in sorted(lots.items(), key=lambda p: p[0].key) if queue)
    if any(b.historical_basis is None for b in balances):
        issues.add('unknown_inventory_basis')
    if unknown_profit:
        issues.add('incomplete_realized_profit')
    if unknown_cash:
        issues.add('incomplete_cash_flow')
    return LedgerResult(balances, None if unknown_profit else known_profit, known_profit,
                        None if unknown_cash else known_cash, known_cash, estimate,
                        None if unknown_profit or estimate is None else known_profit - estimate, tuple(sorted(issues)))


MAX_JOURNAL_BYTES = 256 * 1024


def encode_journal(journal: Journal) -> bytes:
    payload = dumps(journal).encode('utf-8')
    require(len(payload) <= MAX_JOURNAL_BYTES, 'LEDGER_SIZE', 'Journal exceeds 256 KiB')
    return payload


def decode_journal(payload: bytes, catalog: Catalog) -> Journal:
    require(type(payload) is bytes and len(payload) <= MAX_JOURNAL_BYTES, 'LEDGER_SIZE', 'Journal exceeds 256 KiB')
    try:
        journal = loads(Journal, payload.decode('utf-8'))
    except UnicodeError:
        require(False, 'LEDGER_FORMAT', 'Journal must be UTF-8 JSON')
    evaluate_journal(journal, catalog)
    return journal


class LedgerStore:
    """Separate database; immutable append-only revisions with optimistic writes."""
    APPLICATION_ID = 0x41494C34

    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        try:
            with self.connection:
                self.connection.execute('BEGIN IMMEDIATE')
                app = self.connection.execute('PRAGMA application_id').fetchone()[0]
                tables = self.connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                require(app == self.APPLICATION_ID or (app == 0 and not tables), 'LEDGER_DATABASE', 'Choose a separate ledger database')
                require(self.connection.execute('PRAGMA user_version').fetchone()[0] <= 1, 'LEDGER_VERSION', 'Ledger database is newer')
                self.connection.execute('CREATE TABLE IF NOT EXISTS journals (name TEXT, revision INTEGER, payload BLOB NOT NULL, PRIMARY KEY(name, revision))')
                self.connection.execute(f'PRAGMA application_id={self.APPLICATION_ID}')
                self.connection.execute('PRAGMA user_version=1')
        except BaseException:
            self.connection.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.connection.close()

    def load(self, name, catalog):
        row = self.connection.execute('SELECT revision, payload FROM journals WHERE name=? ORDER BY revision DESC LIMIT 1', (name,)).fetchone()
        require(row is not None, 'LEDGER_NOT_FOUND', 'Journal not found')
        return row[0], decode_journal(row[1], catalog)

    def save(self, journal, catalog, expected_revision=0):
        evaluate_journal(journal, catalog)
        payload = encode_journal(journal)
        require(type(expected_revision) is int and expected_revision >= 0, 'LEDGER_REVISION', 'Expected revision must be nonnegative')
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            row = self.connection.execute('SELECT revision, payload FROM journals WHERE name=? ORDER BY revision DESC LIMIT 1', (journal.name,)).fetchone()
            current = 0 if row is None else row[0]
            require(current == expected_revision, 'CONCURRENT_CHANGE', 'Journal changed; reload before appending')
            if row is not None:
                prior = decode_journal(row[1], catalog)
                require(journal.market == prior.market and journal.cost_method == prior.cost_method and journal.estimated_profit == prior.estimated_profit
                        and journal.records[:len(prior.records)] == prior.records,
                        'IMMUTABLE_RECORD', 'Prior records cannot change or disappear; use a separately named corrected journal')
            self.connection.execute('INSERT INTO journals VALUES (?,?,?)', (journal.name, current + 1, payload))
        return current + 1
