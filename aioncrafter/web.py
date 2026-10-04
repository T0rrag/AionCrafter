"""Local manual calculator. Run: python3 -m aioncrafter.web --catalog FILE."""
import argparse
from dataclasses import replace
import secrets
from datetime import datetime, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .catalog import import_catalog
from .codec import ValidationError, require, dumps
from .economics import SaleFees, amount, item_economics, materials_cost
from .identity import Currency, FactionMode, MarketKind, MarketScope, PriceIdentity, normalize_alias
from .manual import manual_observation, resolve_list
from .models import CraftFee, FeeBasis, ItemQuantity, Money, PriceType
from .references import import_references, validate_references, reference_label
from .valuation import HistoricalCost, InventoryEntry, value_materials


def observation_time(form, index, old=None):
    value = form.get(f't{index}', '')
    if value or (old and old.price_type is not PriceType.MANUAL and old.observed_at is None):
        return value
    return form.get('observed', '')


def form_observations(catalog, form, previous=()):
    market = MarketScope(catalog.scope.dataset_kind, catalog.scope.region, MarketKind(form.get('market_kind', '')),
                        form.get('market', ''), FactionMode(form.get('faction_mode', '')), form.get('faction') or None,
                        Currency(catalog.scope.namespace, form.get('currency', ''), int(form.get('precision', ''))))
    if form.get('reference_payload'):
        previous = import_references(form['reference_payload'], catalog, market)
    prior = {obs.identity: obs for obs in previous}
    result = []
    for i, item in enumerate(catalog.items):
        identity = PriceIdentity(item.identity, market)
        price = form.get(f'p{i}', '') or None
        old = prior.get(identity)
        observed = observation_time(form, i, old)
        if old and old.unit_price == price and (old.observed_at or '') == observed:
            result.append(old)
        else:
            new = manual_observation(item.identity, market, price, observed, catalog.provenance)
            result.append(replace(new, supersedes_id=old.observation_id if old else None))
    return tuple(result)


def render(catalog, form=None, *, supplied_observations=None):
    form = form or {}
    def value(name, default=''):
        return form.get(name, default)
    def field(name, label, default='', kind='text', required=False):
        return f'<label>{escape(label)}<input name="{name}" type="{kind}" value="{escape(value(name, default), quote=True)}" {"required" if required else ""}></label>'
    def label(item):
        return f'{item.aliases[0].text} · {item.identity.variant.quality} · +{item.identity.variant.enhancement} · {item.identity.variant.tradability.value}'
    def options(items, selected):
        return ''.join(f'<option value="{i}" {"selected" if str(i)==selected else ""}>{escape(label(item))}</option>' for i, item in items)
    result = ''
    observations = None
    try:
        if form and value('action') != 'search':
            market = MarketScope(catalog.scope.dataset_kind, catalog.scope.region, MarketKind(value('market_kind')),
                                 value('market'), FactionMode(value('faction_mode')), value('faction') or None,
                                 Currency(catalog.scope.namespace, value('currency'), int(value('precision'))))
            observations = form_observations(catalog, form) if supplied_observations is None else supplied_observations
            require(len(observations) == len(catalog.items), 'PLAN_OBSERVATIONS', 'Observation count differs from catalog')
            for i, (item, obs) in enumerate(zip(catalog.items, observations)):
                require(obs.identity == PriceIdentity(item.identity, market) and obs.unit_price == (value(f'p{i}') or None)
                        and (obs.observed_at or '') == observation_time(form, i, obs), 'PLAN_OBSERVATIONS', 'Saved observation differs from form scope, price or time')
            validate_references(observations, catalog, market)
            inventory, history = [], []
            for i, item in enumerate(catalog.items):
                owned = value(f'owned{i}', '0')
                require(owned.isascii() and owned.isdigit(), 'QUANTITY', 'Owned quantity must be a nonnegative integer')
                inventory.append(InventoryEntry(item.identity, int(owned)))
                if value(f'hcost{i}') != '':
                    history.append(HistoricalCost(PriceIdentity(item.identity, market), int(value(f'hqty{i}')),
                                                  Money(value(f'hcost{i}'), market.currency), value(f'href{i}')))
            item_result = None
            if value('workflow') == 'materials':
                entries = []
                pasted = value('paste')
                if pasted.strip():
                    for n, (quantity, candidates) in enumerate(resolve_list(catalog, pasted, value('language', 'en'))):
                        if len(candidates) > 1:
                            selected = value(f'pick{n}')
                            allowed = [(i, item) for i, item in enumerate(catalog.items) if item in candidates]
                            if selected not in [str(i) for i, _ in allowed]:
                                result += f'<label>Choose variant for pasted row {n+1}<select name="pick{n}"><option value="">Choose…</option>{options(allowed, selected)}</select></label>'
                                continue
                            chosen = catalog.items[int(selected)]
                        else:
                            chosen = candidates[0]
                        entries.append(ItemQuantity(chosen.identity, quantity))
                    require(not result, 'AMBIGUOUS_ALIAS', 'Choose each variant above, then calculate again')
                else:
                    for i, item in enumerate(catalog.items):
                        q = value(f'q{i}', '0')
                        require(q.isascii() and q.isdigit(), 'QUANTITY', 'Quantities must be nonnegative integers')
                        if int(q):
                            entries.append(ItemQuantity(item.identity, int(q)))
                calculation = materials_cost(tuple(entries), market, observations)
                result += '<h2>Materials estimate</h2>'
            else:
                recipe = next((r for r in catalog.recipes if r.recipe_id == value('recipe')), None)
                require(recipe is not None, 'RECIPE', 'Select a recipe')
                target_index = int(value('product'))
                require(0 <= target_index < len(catalog.items), 'OUTPUT', 'Choose a product')
                fees = SaleFees(value('tax'), value('sale_fee'), value('rounding'), value('fee_source'))
                override = None
                if value('craft_fee') != '':
                    override = (CraftFee(Money(value('craft_fee'), market.currency), FeeBasis(value('craft_basis'))),)
                r = item_economics(recipe, ItemQuantity(catalog.items[target_index].identity, int(value('target'))),
                                   market, observations, value('selling') or None, fees, override)
                calculation = r.materials
                item_result = r
                result += f'<h2>Item economics</h2><p>{r.crafts} crafts · {r.produced} produced · {r.planned_sales} planned sales · {r.leftovers} unsold leftovers</p>'
                for title, total in [('Craft cost', r.craft_cost), ('Net proceeds', r.proceeds), ('Estimated profit/loss', r.profit), ('Minimum break-even unit price', r.minimum_break_even_price)]:
                    result += f'<p>{title}: {"Unknown / undefined" if total is None else amount(total, market)}</p>'
                roi = 'Undefined' if r.roi_percent is None else f'{r.roi_percent.numerator}/{r.roi_percent.denominator}% (exact)'
                result += f'<p>ROI: {roi}</p><p>{escape(", ".join(r.issues))}</p><p>All craft costs charged to planned sales; leftovers and coproducts have zero credited revenue. Direct ingredients only. Requirements must be checked manually.</p>'
            valuation = value_materials(calculation, market, tuple(inventory), tuple(history))
            cash = valuation.additional_cash
            if item_result is not None:
                cash = None if cash is None or item_result.crafting_fees is None else cash + item_result.crafting_fees
            result += '<h3>Cost views</h3><p>Additional cash required' + (' including assumed crafting fees' if item_result else '') + ': ' + ('Incomplete' if cash is None else amount(cash, market)) + '</p>'
            result += '<p>Recorded consumed-material cost: ' + ('Incomplete — supply records for every consumed unit' if valuation.recorded_total is None else amount(valuation.recorded_total, market)) + '</p>'
            result += '<p>Owned inputs reduce additional cash only. Replacement cost and estimated profit retain their full value. Recorded material costs exclude crafting/sale fees and do not establish realized profit.</p>'
            result += '<table><tr><th>Material</th><th>Required</th><th>Owned used</th><th>To buy</th><th>Unit reference</th><th>Replacement subtotal</th><th>Source and age</th></tr>'
            for line, valued in zip(calculation.lines, valuation.lines):
                item = next(x for x in catalog.items if x.identity == line.item.item)
                result += f'<tr><td>{escape(label(item))}</td><td>{line.item.quantity}</td><td>{valued.owned_used}</td><td>{valued.to_buy}</td><td>{escape((line.observation.unit_price if line.observation else None) or "Unavailable")}</td><td>{"Missing" if line.subtotal is None else amount(line.subtotal, market)}</td><td>{escape(reference_label(line.observation))}</td></tr>'
            result += f'</table><p>Total: {"Incomplete" if calculation.total is None else amount(calculation.total, market)}; known subtotal: {amount(calculation.known_subtotal, market)} {escape(market.currency.code)}</p>'
            result += '<p>Manual references and approved offline references; stock and sell-through unverified. Default observation: ' + escape(value('observed')) + '</p>'
    except (ValidationError, ValueError, StopIteration) as exc:
        result += f'<p role="alert">{escape(str(exc))}</p>'
    select = lambda name, vals, default: f'<label>{name}<select name="{name}">' + ''.join(f'<option {"selected" if value(name,default)==x else ""}>{x}</option>' for x in vals) + '</select></label>'
    body = '<h1>AionCrafter · Manual calculator</h1><p><strong>' + escape(catalog.scope.dataset_kind.value) + '</strong> · ' + escape(catalog.scope.region + ' / ' + catalog.scope.build) + ' · Gate A/B UNVERIFIED</p><p>Fees are user assumptions, unverified for the game. Blank prices stay unavailable. No prices or fees are prefilled. Use local saved plans to keep prices and inputs between sessions. Snapshots are delayed references, never live prices.</p><form method="post">'
    body += select('workflow', ['materials', 'item'], 'materials')
    body += '<fieldset><legend>Explicit market and observation</legend>'
    body += field('market', 'Market ID', required=True) + select('market_kind', ['server','group'], 'server')
    body += select('faction_mode', ['not_applicable','specific'], 'not_applicable') + field('faction', 'Faction ID (when specific)')
    body += field('currency','Currency code', required=True) + field('precision','Currency decimals','2','number',True)
    body += field('observed','Observed at (ISO 8601 with timezone)',required=True) + '</fieldset>'
    if supplied_observations is not None:
        body += '<input type="hidden" name="reference_payload" value="' + escape(dumps(supplied_observations), quote=True) + '">'
    elif value('reference_payload'):
        body += '<input type="hidden" name="reference_payload" value="' + escape(value('reference_payload'), quote=True) + '">'
    body += '<fieldset><legend>Unit references and materials-only quantities</legend>'
    for i, item in enumerate(catalog.items):
        source = supplied_observations if supplied_observations is not None else observations
        current = source[i] if source and i < len(source) else None
        body += '<div>' + field(f'p{i}', label(item) + ' — unit price') + '<p class="reference-source">' + escape(reference_label(current)) + '</p>' + field(f't{i}', 'Item observed at (blank uses default; imported unknown remains unknown)', value('observed')) + field(f'q{i}', 'Quantity', '0','number') + field(f'owned{i}', 'Owned usable quantity', '0', 'number') + '<details><summary>Recorded consumed-material cost</summary>' + field(f'hqty{i}', 'Recorded consumed quantity', '', 'number') + field(f'hcost{i}', 'Recorded total paid for those units') + field(f'href{i}', 'Record reference') + '</details></div>'
    body += '<label>Paste quantity TAB exact name per line<textarea name="paste">' + escape(value('paste')) + '</textarea></label>'
    body += select('language',['en','es'],'en') + '</fieldset><fieldset><legend>Item workflow (ignored in materials mode)</legend>'
    query = value('product_search').strip()
    products = list(enumerate(catalog.items))
    if query:
        try:
            term = normalize_alias(query)
            products = [(i,item) for i,item in products if any(term in normalize_alias(a.text) for a in item.aliases)]
        except ValidationError:
            products = []
    body += field('product_search', 'Search product (English or Spanish)') + '<button name="action" value="search" formnovalidate>Search products</button>'
    body += '<label>Product<select name="product">' + options(products, value('product')) + '</select></label>'
    if not products:
        body += '<p>No matching product. Change the search text.</p>'
    body += '<label>Recipe<select name="recipe">' + ''.join(f'<option value="{escape(r.recipe_id)}" {"selected" if value("recipe")==r.recipe_id else ""}>{escape(r.recipe_id)}</option>' for r in catalog.recipes) + '</select></label>'
    body += field('target','Planned sell quantity','1','number') + field('selling','Selling unit price')
    body += field('craft_fee','Explicit craft-fee override (blank uses catalog; 0 explicitly waives)')
    body += select('craft_basis',['per_attempt','per_batch','per_output_unit'],'per_batch')
    body += field('tax','Sale tax fraction (0 through 1)') + field('sale_fee','Total listing / other sale fees')
    body += select('rounding',['floor','ceil','half_up'],'floor') + field('fee_source','Fee source / unverified assumption') + '</fieldset>'
    body += '<fieldset><legend>Approved offline references</legend><p>Paste a JSON array of PriceObservation records from a source you are permitted to use. Synthetic references remain synthetic. Snapshot time may be unknown; import time never establishes freshness. Vendor stock and restrictions must be checked manually. Editing price/time creates a linked manual override.</p><textarea name="reference_data"></textarea><button name="action" value="references">Preview reference import</button></fieldset>'
    body += '<button>Calculate</button><section aria-live="polite">' + result + '</section></form>'
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>AionCrafter manual calculator</title><style>body{font:16px system-ui;max-width:1050px;margin:2rem auto;padding:0 1rem;background:#101827;color:#e5edf8}fieldset{margin:1rem 0;border:1px solid #506078}label{display:inline-block;margin:.5rem}input,select,textarea,button{display:block;font:inherit;padding:.5rem;max-width:90%}table{border-collapse:collapse}td,th{padding:.5rem;border:1px solid #506078}button{cursor:pointer;background:#8ce5c0} [role=alert]{color:#ffbaad}</style>' + body + '</html>'


def handler(catalog, plan_database=None):
    from .plans import PlanStore, SavedPlan, catalog_digest, decode_plan, encode_plan
    token = secrets.token_urlsafe(32)
    reserved = {'action','csrf','plan_name','revision','favorite','import_data','import_format','confirm_delete','import_payload','reference_data','reference_payload'}

    class Handler(BaseHTTPRequestHandler):
        def allowed_host(self):
            return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

        def page(self, form=None, *, notice='', observations=None):
            form = form or {}
            if form and observations is None:
                try:
                    observations = form_observations(catalog, form)
                    validate_references(observations, catalog, observations[0].identity.market)
                except (ValidationError, ValueError):
                    observations = None
            html = render(catalog, form or None, supplied_observations=observations)
            controls = f'<input type="hidden" name="csrf" value="{token}">'
            if form.get('import_payload'):
                controls += '<input type="hidden" name="import_payload" value="' + escape(form['import_payload'], quote=True) + '">'
            if plan_database:
                with PlanStore(plan_database) as store:
                    plans = store.list()
                controls += '<fieldset><legend>Local saved plans</legend><p>Save prices, market settings, quantities, inventory and cost records on this computer. Export before deleting.</p>'
                controls += '<label>Plan name<input name="plan_name" value="' + escape(form.get('plan_name',''), quote=True) + '"></label>'
                controls += '<input type="hidden" name="revision" value="' + escape(form.get('revision','0'), quote=True) + '">'
                controls += '<label><input type="checkbox" name="favorite" value="yes" ' + ('checked' if form.get('favorite') == 'yes' else '') + '>Favorite</label>'
                controls += '<button name="action" value="save">Save plan</button><button name="action" value="load" formnovalidate>Load named plan</button><button name="action" value="export_json" formnovalidate>Export JSON</button><button name="action" value="export_csv" formnovalidate>Export CSV</button>'
                controls += '<p>Saved names: ' + escape(', '.join(name for name,_ in plans) or 'None') + '</p>'
                controls += '<label>Paste exported plan JSON or CSV<textarea name="import_data"></textarea></label><label>Import format<select name="import_format"><option>json</option><option>csv</option></select></label><button name="action" value="import" formnovalidate>Preview import</button>'
                controls += '<label><input type="checkbox" name="confirm_delete" value="yes">Delete all revisions of this named plan</label><p>Deletion removes plan contents; a name/revision counter remains to reject stale tabs.</p><button name="action" value="delete" formnovalidate>Delete named plan</button><button name="action" value="reset" formnovalidate>Reset unsaved form</button></fieldset>'
            html = html.replace('<form method="post">', '<form method="post">' + controls)
            if notice:
                html = html.replace('<h1>', '<p role="status">' + escape(notice) + '</p><h1>', 1)
            self.reply(html)

        def do_GET(self):
            if not self.allowed_host():
                self.send_error(403)
                return
            if urlsplit(self.path).path != '/':
                self.send_error(404)
                return
            self.page()

        def do_POST(self):
            if not self.allowed_host() or (self.headers.get('Origin') and self.headers['Origin'] != 'http://' + self.headers.get('Host', '')):
                self.send_error(403)
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= (1024 * 1024 if plan_database else 65536):
                    self.send_error(413)
                    return
                data = parse_qs(self.rfile.read(size).decode('utf-8'), keep_blank_values=True, max_num_fields=200)
                require(all(len(v) == 1 for v in data.values()), 'DUPLICATE_FIELD', 'Form fields repeat')
                form = {k:v[0] for k,v in data.items()}
                action = form.get('action', 'calculate')
                if action == 'references':
                    previous = form_observations(catalog, form)
                    imported = import_references(form.get('reference_data',''), catalog, previous[0].identity.market)
                    merged = {o.identity: o for o in previous}
                    merged.update({o.identity: o for o in imported})
                    observations = tuple(merged[o.identity] for o in previous)
                    validate_references(observations, catalog, previous[0].identity.market)
                    for i, obs in enumerate(observations):
                        form[f'p{i}'] = obs.unit_price or ''
                        form[f't{i}'] = obs.observed_at or ''
                    self.page(form, notice='Reference import validated. Review source, rights, time and quantities before saving.', observations=observations)
                    return
                if action in ('calculate', 'search'):
                    self.page(form)
                    return
                require(plan_database is not None, 'PLAN_STORAGE', 'Saved plans are disabled')
                require(secrets.compare_digest(form.get('csrf',''), token), 'CSRF', 'Reload this page before changing saved plans')
                if action == 'reset':
                    self.page(notice='Unsaved form reset. Saved plans retained.')
                    return
                if action == 'import':
                    plan = decode_plan(form.get('import_data','').encode(), catalog, form.get('import_format','json'))
                    restored = dict(plan.fields, plan_name=plan.name, favorite='yes' if plan.favorite else '', revision='0', import_payload=encode_plan(plan).decode())
                    self.page(restored, notice='Import validated. Review and save under a new name, or load the existing plan first to update it.', observations=plan.observations)
                    return
                with PlanStore(plan_database) as store:
                    name = form.get('plan_name','')
                    if action in ('load','export_json','export_csv'):
                        revision, plan = store.load(name, catalog)
                        if action.startswith('export_'):
                            format = action.removeprefix('export_')
                            self.reply(encode_plan(plan, format), content_type='application/json' if format == 'json' else 'text/csv', filename='aioncrafter-plan.'+format)
                        else:
                            restored = dict(plan.fields, plan_name=plan.name, favorite='yes' if plan.favorite else '', revision=str(revision))
                            self.page(restored, notice='Loaded saved plan; original observation times retained.', observations=plan.observations)
                        return
                    revision = int(form.get('revision','0'))
                    if action == 'delete':
                        require(form.get('confirm_delete') == 'yes', 'CONFIRM_DELETE', 'Select the explicit delete confirmation')
                        store.delete(name, revision)
                        self.page(notice='Named plan and its revisions deleted. Other plans retained.')
                        return
                    require(action == 'save', 'ACTION', 'Unknown action')
                    previous = store.load(name, catalog)[1].observations if revision else ()
                    if not revision and form.get('import_payload'):
                        previous = decode_plan(form['import_payload'].encode(), catalog).observations
                    fields = tuple(sorted((k,v) for k,v in form.items() if k not in reserved))
                    observations = form_observations(catalog, form, previous)
                    plan = SavedPlan(1, name, form.get('favorite') == 'yes', catalog.release_id, catalog_digest(catalog),
                                     fields, observations, datetime.now(timezone.utc).isoformat())
                    revision = store.save(plan, catalog, revision)
                    form['revision'] = str(revision)
                    form.pop('import_payload', None)
                    self.page(form, notice='Saved locally at revision ' + str(revision), observations=observations)
            except (ValueError, UnicodeError) as exc:
                self.page(form if 'form' in locals() else None, notice=str(exc))

        def reply(self, text, *, content_type='text/html; charset=utf-8', filename=None):
            payload = text if type(text) is bytes else text.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(payload)))
            if filename:
                self.send_header('Content-Disposition', 'attachment; filename="' + filename + '"')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(payload)
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', required=True, type=Path)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--plans', type=Path, default=Path('local-data/plans.sqlite3'))
    args = parser.parse_args()
    catalog = import_catalog(args.catalog.read_bytes())
    print(f'Local calculator: http://127.0.0.1:{args.port} ({catalog.scope.dataset_kind.value})', flush=True)
    args.plans.parent.mkdir(parents=True, exist_ok=True)
    with HTTPServer(('127.0.0.1', args.port), handler(catalog, str(args.plans))) as server:
        server.serve_forever()


if __name__ == '__main__':
    main()
