"""Local actual-record form; preview explicitly before writing a journal revision."""
from dataclasses import replace
from html import escape
import sqlite3
from uuid import uuid4

from .codec import ValidationError, require
from .identity import Currency, FactionMode, MarketKind, MarketScope
from .ledger import (CraftRecord, Journal, LedgerStore, OutputShare, RecordSource, SaleRecord,
                     StockRecord, decode_journal, encode_journal, evaluate_journal)
from .models import ItemQuantity, Money
from .plans import catalog_digest
from .stochastic_view import exact_expected


def ledger_page(catalog, form, token, database):
    form = dict(form)
    journal, notice, result = None, '', None
    try:
        action = form.get('action', '')
        if action in ('load', 'export'):
            require(database is not None, 'LEDGER_STORAGE', 'Local storage is disabled')
            with LedgerStore(database) as store:
                revision, journal = store.load(form.get('journal_name', ''), catalog)
            form['revision'] = str(revision)
            if action == 'export':
                return encode_journal(journal), True
            notice = 'Loaded saved journal. Existing records are immutable; new records append.'
        elif action == 'import':
            journal = decode_journal(form.get('import_data', '').encode('utf-8'), catalog)
            form['revision'] = '0'
            form['journal_name'] = journal.name
            notice = 'Import validated, not saved. Use a new name to copy; load an existing journal before appending.'
        else:
            if form.get('journal_payload'):
                journal = decode_journal(form['journal_payload'].encode('utf-8'), catalog)
                journal = replace(journal, name=form.get('journal_name', journal.name))
            if action == 'preview_record':
                if journal is None:
                    market = MarketScope(catalog.scope.dataset_kind, catalog.scope.region, MarketKind(form.get('market_kind', '')),
                                         form.get('market', ''), FactionMode(form.get('faction_mode', '')), form.get('faction') or None,
                                         Currency(catalog.scope.namespace, form.get('currency', ''), int(form.get('precision', ''))))
                    estimate = Money(form['estimate_profit'], market.currency) if form.get('estimate_profit') else None
                    journal = Journal(1, form.get('journal_name', ''), catalog_digest(catalog), market, 'fifo', (), estimate)
                source = RecordSource(str(uuid4()), form.get('occurred', ''), form.get('record_ref', ''))
                def money(key):
                    return Money(form[key], journal.market.currency) if form.get(key) else None
                kind = form.get('record_kind')
                if kind == 'craft':
                    consumed, produced, shares = [], [], []
                    for i, item in enumerate(catalog.items):
                        for prefix, entries in (('consumed', consumed), ('produced', produced)):
                            quantity = form.get(f'{prefix}{i}', '') or '0'
                            require(quantity.isascii() and quantity.isdigit(), 'QUANTITY', 'Actual quantities must be nonnegative integers')
                            if int(quantity):
                                entries.append(ItemQuantity(item.identity, int(quantity)))
                        if form.get(f'share{i}'):
                            shares.append(OutputShare(item.identity, form[f'share{i}']))
                    record = CraftRecord(source, tuple(consumed), tuple(produced), money('paid_fee'), tuple(shares) if shares else None)
                else:
                    index = int(form.get('record_item', ''))
                    require(0 <= index < len(catalog.items), 'OUTPUT', 'Choose an actual item variant')
                    quantity = ItemQuantity(catalog.items[index].identity, int(form.get('record_quantity', '')))
                    if kind == 'sale':
                        record = SaleRecord(source, quantity, money('received'), money('paid_fee'))
                    else:
                        record = StockRecord(source, kind, quantity, money('paid_total'))
                journal = replace(journal, records=journal.records + (record,))
                evaluate_journal(journal, catalog)
                notice = 'Actual record appended to the unsaved preview. Review, then save this revision.'
            elif action == 'save':
                require(database is not None and journal is not None, 'LEDGER_STORAGE', 'Preview records before saving')
                with LedgerStore(database) as store:
                    revision = store.save(journal, catalog, int(form.get('revision', '0')))
                form['revision'] = str(revision)
                notice = f'Journal saved locally at revision {revision}.'
            else:
                require(action == '', 'ACTION', 'Unknown journal action')
        if journal is not None:
            result = evaluate_journal(journal, catalog)
            form['journal_payload'] = encode_journal(journal).decode('utf-8')
    except (ValueError, sqlite3.Error, OSError) as exc:
        notice = ('STORAGE_UNAVAILABLE: The operation could not be confirmed. The last valid preview is retained; reload the saved revision before retrying.'
                  if isinstance(exc, (sqlite3.Error, OSError)) else str(exc))
        # Preserve the last valid preview; never turn a failed appended record into
        # a hidden payload that a later save could accidentally accept.
        try:
            journal = decode_journal(form['journal_payload'].encode('utf-8'), catalog) if form.get('journal_payload') else None
        except (ValidationError, ValueError):
            journal = None
            form.pop('journal_payload', None)
        result = evaluate_journal(journal, catalog) if journal is not None else None
    def historical(value):
        return exact_expected(value, journal.market, label='exact historical amount')
    def field(key, label, default='', kind='text'):
        return '<label>' + escape(label) + '<input name="' + key + '" type="' + kind + '" value="' + escape(form.get(key, default), quote=True) + '"></label>'
    def select(key, choices, default):
        return '<label>' + escape(key) + '<select name="' + key + '">' + ''.join('<option ' + ('selected' if form.get(key, default) == choice else '') + '>' + choice + '</option>' for choice in choices) + '</select></label>'
    html = '<!doctype html><html lang="en"><meta charset="utf-8"><title>AionCrafter actual records</title><style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}fieldset{margin:1rem 0}label{display:inline-block;margin:.5rem}input,select,textarea,button{display:block;padding:.5rem}td,th{border:1px solid #aaa;padding:.4rem}table{border-collapse:collapse}</style><a href="/">Back to calculator</a><h1>Actual records</h1><p>'
    html += escape(catalog.scope.dataset_kind.value + ' / ' + catalog.scope.build) + ' · FIFO historical cost. No market estimates are substituted for missing records. Profit includes recorded failed-craft expenses; unsold stock retains its cost. Exact fractional cost allocations are not rounded.</p>'
    html += '<p role="status">' + escape(notice) + '</p><form method="post"><input type="hidden" name="csrf" value="' + token + '">'
    html += '<input type="hidden" name="revision" value="' + escape(form.get('revision', '0'), quote=True) + '">'
    html += '<input type="hidden" name="journal_payload" value="' + escape(form.get('journal_payload', ''), quote=True) + '">'
    html += field('journal_name', 'Journal name')
    html += '<button name="action" value="load">Load named journal</button><button name="action" value="save">Save preview</button><button name="action" value="export">Export saved journal</button>'
    if journal is None:
        html += '<fieldset><legend>New journal market (fixed after the first record)</legend>'
        html += field('market', 'Market ID') + select('market_kind', ('server', 'group'), 'server')
        html += select('faction_mode', ('not_applicable', 'specific'), 'not_applicable') + field('faction', 'Faction ID')
        html += field('currency', 'Currency code') + field('precision', 'Currency decimals', '2', 'number')
        html += field('estimate_profit', 'Original estimated profit / loss for this journal (optional; negative allowed)') + '</fieldset>'
    else:
        html += '<p>Fixed market: ' + escape(journal.market.market_id + ' / ' + journal.market.currency.code) + f' · {len(journal.records)} actual records</p>'
    html += '<fieldset><legend>Add an actual record</legend>'
    html += select('record_kind', ('opening', 'purchase', 'craft', 'sale'), 'purchase')
    html += field('occurred', 'Occurred at (ISO timestamp with timezone)') + field('record_ref', 'Actual receipt / activity reference')
    html += '<p>Opening stock must come first. Blank money is unknown; enter 0 only when explicitly zero. Preview does not write to storage.</p><label>Item for opening stock / purchase / sale<select name="record_item">'
    for i, item in enumerate(catalog.items):
        html += '<option value="' + str(i) + '" ' + ('selected' if form.get('record_item', '0') == str(i) else '') + '>' + escape(f'{item.aliases[0].text} · {item.identity.variant.quality} · +{item.identity.variant.enhancement} · {item.identity.variant.tradability.value}') + '</option>'
    html += '</select></label>' + field('record_quantity', 'Actual quantity', '', 'number')
    html += field('paid_total', 'Total purchase / opening historical cost, including acquisition fees')
    html += field('received', 'Gross sale proceeds actually received') + field('paid_fee', 'Actual craft or sale fees')
    html += '<details><summary>Actual craft consumption and outputs</summary><p>Record what happened, including failure. Leave outputs at zero for failure. For multiple outputs, explicit cost shares must sum to 1; blank shares leave their historical basis unknown. A single output inherits all consumed cost.</p>'
    for i, item in enumerate(catalog.items):
        html += '<p>' + escape(f'{item.aliases[0].text} / {item.identity.item_id} / {item.identity.variant.quality} / +{item.identity.variant.enhancement} / {item.identity.variant.tradability.value}') + '</p>'
        html += field(f'consumed{i}', 'Consumed quantity', '0', 'number') + field(f'produced{i}', 'Produced quantity', '0', 'number') + field(f'share{i}', 'Output cost share (0 to 1)')
    html += '</details><button name="action" value="preview_record">Add to preview</button></fieldset>'
    html += '<details><summary>Import exported journal</summary><textarea name="import_data"></textarea><button name="action" value="import">Preview import</button></details></form>'
    if result is not None:
        html += '<h2>Recorded result</h2><p>Realized profit / loss: ' + historical(result.realized_profit) + '</p><p>Net cash flow during this journal: ' + historical(result.net_cash_flow) + '</p>'
        html += '<p>Original recorded estimate: ' + historical(result.recorded_estimate) + '; realized less estimate so far: ' + historical(result.realized_less_estimate) + '. Unsold stock is excluded from realized profit; this is not a final comparison while the planned activity is unfinished.</p>'
        html += '<p>' + escape(', '.join(result.issues)) + '</p><table><tr><th>Remaining item</th><th>Quantity</th><th>Historical basis</th></tr>'
        names = {item.identity: item.aliases[0].text for item in catalog.items}
        for balance in result.inventory:
            html += '<tr><td>' + escape(names[balance.item]) + '</td><td>' + str(balance.quantity) + '</td><td>' + historical(balance.historical_basis) + '</td></tr>'
        html += '</table><h3>Record history</h3><ol>'
        for record in journal.records:
            kind = record.kind if type(record) is StockRecord else 'craft' if type(record) is CraftRecord else 'sale'
            html += '<li>' + escape(f'{kind} · {record.source.occurred_at} · {record.source.reference} · {record.source.record_id}') + '</li>'
        html += '</ol>'
    return html + '</html>', False
