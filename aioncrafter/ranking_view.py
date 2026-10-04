"""Offline ranking controls and conditional route table."""
from datetime import datetime, timezone
from html import escape

from .buycraft import compare_routes
from .codec import require
from .economics import SaleFees, amount
from .manual import manual_observation
from .models import Money
from .ranking import CraftCandidate, RankingPolicy, RecipeAccess, rank_crafts
from .references import reference_label


def ranking_controls(catalog, form):
    def field(key, label, kind='text'):
        return '<label>' + escape(label) + '<input name="' + key + '" type="' + kind + '" value="' + escape(form.get(key, ''), quote=True) + '"></label>'
    def lines(key, label):
        return '<label>' + escape(label) + '<textarea name="' + key + '">' + escape(form.get(key, '')) + '</textarea></label>'
    html = '<fieldset><legend>Conditional ranking (rank mode only)</legend><p>Ranks routes for the chosen product and quantity. Recipe profession and eligibility are explicit user attestations; this app does not verify game rules.</p>'
    html += field('rank_budget', 'Maximum additional cash including fixed sale fees')
    html += field('rank_age', 'Maximum source age in seconds (explicit policy)', 'number')
    html += field('selling_observed', 'Selling price observed at (blank uses the default observation time)')
    html += lines('rank_professions', 'Allowed professions, one exact name per line')
    html += lines('vendor_confirmed', 'Confirmed vendor restrictions, one exact recorded restriction per line')
    html += '<label>Sort by<select name="rank_sort">' + ''.join('<option ' + ('selected' if form.get('rank_sort', 'profit') == v else '') + '>' + v + '</option>' for v in ('profit', 'roi', 'capital')) + '</select></label>'
    for i, recipe in enumerate(catalog.recipes):
        html += '<details><summary>' + escape(recipe.recipe_id) + ' — eligibility</summary>'
        html += field(f'profession{i}', 'Profession') + field(f'profession_ref{i}', 'Profession evidence reference')
        html += '<p>Recorded requirements: ' + escape('Unknown' if recipe.requirements is None else ', '.join(recipe.requirements) or 'None') + '</p>'
        html += lines(f'requirements_ok{i}', 'Confirmed requirements, one exact recorded requirement per line') + '</details>'
    return html + '<p>Profit and ROI charge replacement cost; budget uses additional cash after stock plus fixed sale fees. Results remain conditional estimates. Unconfirmed, incomplete, stale and over-budget routes are shown as excluded.</p></fieldset>'


def render_ranking(catalog, form, target, chosen, market, observations, inventory, overrides):
    require(len(chosen) <= 7, 'PLANNING_LIMIT', 'Choose at most 7 candidate recipes for ranking')
    now = datetime.now(timezone.utc)
    def lines(key):
        return tuple(s.strip() for s in form.get(key, '').splitlines() if s.strip())
    access = tuple(RecipeAccess(r.recipe_id, form.get(f'profession{i}') or None,
                               form.get(f'profession_ref{i}') or None, lines(f'requirements_ok{i}')) for i, r in enumerate(catalog.recipes))
    policy = RankingPolicy(Money(form.get('rank_budget', ''), market.currency), lines('rank_professions'), access,
                           lines('vendor_confirmed'), int(form.get('rank_age', '')), form.get('rank_sort', 'profit'))
    sale = manual_observation(target.item, market, form.get('selling') or None,
                              form.get('selling_observed') or form.get('observed', ''), catalog.provenance, now=now.isoformat())
    fee_fields = ('tax', 'sale_fee', 'rounding', 'fee_source')
    fees = SaleFees(*(form[key] for key in fee_fields)) if all(form.get(key) for key in fee_fields) else None
    routes = compare_routes(catalog, (target,), chosen, market, observations, objective='additional_cash',
                            inventory=inventory, fee_overrides=overrides, max_routes=128)
    candidates = tuple(CraftCandidate(f'route-{i+1}', target, r.selected_recipes, sale, fees) for i, r in enumerate(routes.routes))
    result = rank_crafts(catalog, candidates, market, observations, policy=policy, now=now, inventory=inventory,
                         fee_overrides=overrides, max_candidates=128)
    html = '<h2>Conditional route ranking</h2><p>' + f'{len(result.ranked)} routes pass the selected filters; {len(result.excluded)} excluded. '
    html += 'All results assume the planned sales occur. This is not a sale guarantee or general optimizer.</p><p>Selling assumption: ' + escape(reference_label(sale, now=now)) + '</p>'
    def money(value):
        return 'Unknown' if value is None else amount(value, market)
    for label, rows in (('Passing estimates', result.ranked), ('Excluded routes', result.excluded)):
        html += '<h3>' + label + '</h3><table><tr><th>Route</th><th>Estimated profit</th><th>Capital required</th><th>ROI</th><th>Price age status</th><th>Exclusions / uncertainty</th></tr>'
        for row in rows:
            roi = 'Undefined' if row.roi_percent is None else f'{row.roi_percent.numerator}/{row.roi_percent.denominator}%'
            html += '<tr><td>' + escape(', '.join(row.candidate.recipe_ids) or 'Buy all') + '</td><td>' + money(row.profit) + '</td><td>' + money(row.capital_required) + '</td><td>' + roi + '</td><td>' + escape(', '.join(row.freshness)) + '</td><td>' + escape(', '.join((*row.excluded_reasons, *row.warnings))) + '</td></tr>'
        html += '</table>'
    html += '<h3>Input reference evidence</h3>'
    used = {o.observation_id: o for row in (*result.ranked, *result.excluded) for o in row.observations if o != sale}
    for obs in used.values():
        html += '<p>' + escape(reference_label(obs, now=now)) + '</p>'
    return html
