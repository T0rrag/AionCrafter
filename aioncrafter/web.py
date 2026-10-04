"""Local manual calculator. Run: python3 -m aioncrafter.web --catalog FILE."""
import argparse
from datetime import datetime, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from .catalog import import_catalog
from .codec import ValidationError, require
from .economics import SaleFees, amount, item_economics, materials_cost
from .identity import Currency, FactionMode, MarketKind, MarketScope
from .manual import manual_observation, resolve_list
from .models import CraftFee, FeeBasis, ItemQuantity, Money


def render(catalog, form=None):
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
    try:
        if form:
            market = MarketScope(catalog.scope.dataset_kind, catalog.scope.region, MarketKind(value('market_kind')),
                                 value('market'), FactionMode(value('faction_mode')), value('faction') or None,
                                 Currency(catalog.scope.namespace, value('currency'), int(value('precision'))))
            observations = tuple(manual_observation(item.identity, market, value(f'p{i}'), value('observed'), catalog.provenance)
                                 for i, item in enumerate(catalog.items))
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
                result += f'<h2>Item economics</h2><p>{r.crafts} crafts · {r.produced} produced · {r.planned_sales} planned sales · {r.leftovers} unsold leftovers</p>'
                for title, total in [('Craft cost', r.craft_cost), ('Net proceeds', r.proceeds), ('Estimated profit/loss', r.profit), ('Minimum break-even unit price', r.minimum_break_even_price)]:
                    result += f'<p>{title}: {"Unknown / undefined" if total is None else amount(total, market)}</p>'
                roi = 'Undefined' if r.roi_percent is None else f'{r.roi_percent.numerator}/{r.roi_percent.denominator}% (exact)'
                result += f'<p>ROI: {roi}</p><p>{escape(", ".join(r.issues))}</p><p>All craft costs charged to planned sales; leftovers and coproducts have zero credited revenue. Direct ingredients only. Requirements must be checked manually.</p>'
            result += '<table><tr><th>Material</th><th>Quantity</th><th>Unit reference</th><th>Subtotal</th></tr>'
            for line in calculation.lines:
                item = next(x for x in catalog.items if x.identity == line.item.item)
                result += f'<tr><td>{escape(label(item))}</td><td>{line.item.quantity}</td><td>{escape(line.observation.unit_price or "Unavailable")}</td><td>{"Missing" if line.subtotal is None else amount(line.subtotal, market)}</td></tr>'
            result += f'</table><p>Total: {"Incomplete" if calculation.total is None else amount(calculation.total, market)}; known subtotal: {amount(calculation.known_subtotal, market)} {escape(market.currency.code)}</p>'
            result += '<p>Manual references; stock and sell-through unverified. Observation: ' + escape(value('observed')) + '</p>'
    except (ValidationError, ValueError, StopIteration) as exc:
        result += f'<p role="alert">{escape(str(exc))}</p>'
    select = lambda name, vals, default: f'<label>{name}<select name="{name}">' + ''.join(f'<option {"selected" if value(name,default)==x else ""}>{x}</option>' for x in vals) + '</select></label>'
    body = '<h1>AionCrafter · Manual calculator</h1><p><strong>' + escape(catalog.scope.dataset_kind.value) + '</strong> · ' + escape(catalog.scope.region + ' / ' + catalog.scope.build) + ' · Gate A/B UNVERIFIED</p><p>Fees are user assumptions, unverified for the game. Blank prices stay unavailable. No prices or fees are prefilled. This Part 01 form keeps values only while resubmitting; it does not save plans.</p><form method="post">'
    body += select('workflow', ['materials', 'item'], 'materials')
    body += '<fieldset><legend>Explicit market and observation</legend>'
    body += field('market', 'Market ID', required=True) + select('market_kind', ['server','group'], 'server')
    body += select('faction_mode', ['not_applicable','specific'], 'not_applicable') + field('faction', 'Faction ID (when specific)')
    body += field('currency','Currency code', required=True) + field('precision','Currency decimals','2','number',True)
    body += field('observed','Observed at (ISO 8601 with timezone)',required=True) + '</fieldset>'
    body += '<fieldset><legend>Manual unit prices and materials-only quantities</legend>'
    for i, item in enumerate(catalog.items):
        body += '<div>' + field(f'p{i}', label(item) + ' — unit price') + field(f'q{i}', 'Quantity', '0','number') + '</div>'
    body += '<label>Paste quantity TAB exact name per line<textarea name="paste">' + escape(value('paste')) + '</textarea></label>'
    body += select('language',['en','es'],'en') + '</fieldset><fieldset><legend>Item workflow (ignored in materials mode)</legend>'
    body += '<label>Product<select name="product">' + options(enumerate(catalog.items), value('product')) + '</select></label>'
    body += '<label>Recipe<select name="recipe">' + ''.join(f'<option value="{escape(r.recipe_id)}" {"selected" if value("recipe")==r.recipe_id else ""}>{escape(r.recipe_id)}</option>' for r in catalog.recipes) + '</select></label>'
    body += field('target','Planned sell quantity','1','number') + field('selling','Selling unit price')
    body += field('craft_fee','Explicit craft-fee override (blank uses catalog; 0 explicitly waives)')
    body += select('craft_basis',['per_attempt','per_batch','per_output_unit'],'per_batch')
    body += field('tax','Sale tax fraction (0 through 1)') + field('sale_fee','Total listing / other sale fees')
    body += select('rounding',['floor','ceil','half_up'],'floor') + field('fee_source','Fee source / unverified assumption') + '</fieldset>'
    body += '<button>Calculate</button><section aria-live="polite">' + result + '</section></form>'
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>AionCrafter manual calculator</title><style>body{font:16px system-ui;max-width:1050px;margin:2rem auto;padding:0 1rem;background:#101827;color:#e5edf8}fieldset{margin:1rem 0;border:1px solid #506078}label{display:inline-block;margin:.5rem}input,select,textarea,button{display:block;font:inherit;padding:.5rem;max-width:90%}table{border-collapse:collapse}td,th{padding:.5rem;border:1px solid #506078}button{cursor:pointer;background:#8ce5c0} [role=alert]{color:#ffbaad}</style>' + body + '</html>'


def handler(catalog):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.reply(render(catalog))
        def do_POST(self):
            if self.headers.get('Origin') and self.headers['Origin'] != 'http://' + self.headers.get('Host', ''):
                self.send_error(403)
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 65536:
                    self.send_error(413)
                    return
                data = parse_qs(self.rfile.read(size).decode('utf-8'), keep_blank_values=True, max_num_fields=200)
                self.reply(render(catalog, {k:v[-1] for k,v in data.items()}))
            except (ValueError, UnicodeError):
                self.send_error(400)
        def reply(self, text):
            payload = text.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(payload)
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', required=True, type=Path)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    catalog = import_catalog(args.catalog.read_bytes())
    print(f'Local calculator: http://127.0.0.1:{args.port} ({catalog.scope.dataset_kind.value})', flush=True)
    with HTTPServer(('127.0.0.1', args.port), handler(catalog)) as server:
        server.serve_forever()


if __name__ == '__main__':
    main()
