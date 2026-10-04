"""Manual one-attempt scenario presentation, with no guessed probability inputs."""
from fractions import Fraction
from html import escape

from .codec import require
from .economics import SaleFees, amount
from .models import Money
from .references import reference_label
from .stochastic import AttemptEvidence, PlannedSale, attempt_economics


def exact_expected(value, market, *, label='exact expected amount'):
    if value is None:
        return 'Unknown'
    value = Fraction(value)
    if value.denominator == 1:
        return amount(value.numerator, market)
    value /= 10 ** market.currency.decimal_places
    return f'{value.numerator}/{value.denominator} {escape(market.currency.code)} ({escape(label)})'


def scenario_controls(catalog, form):
    html = '<fieldset><legend>One-attempt scenarios (scenario mode only)</legend><p>Probabilities come from the catalog; unknown values stay unknown. Evidence fields are your attestations, not verification by this app. For real recipes cite verified rules for this exact build. The planned sell quantity is a cap in each outcome, not a promised yield.</p>'
    html += '<label>Recipe these attestations apply to<select name="attempt_evidence_recipe"><option value="">Choose explicitly</option>'
    html += ''.join('<option value="' + escape(r.recipe_id, quote=True) + '" ' + ('selected' if form.get('attempt_evidence_recipe') == r.recipe_id else '') + '>' + escape(r.recipe_id) + '</option>' for r in catalog.recipes)
    html += '</select></label>'
    for key, title in (('probability_evidence', 'Verified probability evidence (blank keeps expectations unknown)'),
                       ('consumption_evidence', 'Evidence all inputs are consumed on every attempt, including failure (blank keeps cost unknown)')):
        html += '<label>' + title + '<input name="' + key + '" value="' + escape(form.get(key, ''), quote=True) + '"></label>'
    return html + '<p>The local form models the catalog’s mutually exclusive outcomes. Independent bonuses require the separate library contract and evidence; do not enter bonus probabilities as alternative outcomes. Owned stock, recursive choices and historical costs are not applied to this per-attempt replacement-cost view.</p></fieldset>'


def render_scenarios(catalog, form, recipe, target, market, observations, override):
    probability_ref = form.get('probability_evidence') or None
    consumption_ref = form.get('consumption_evidence') or None
    if probability_ref or consumption_ref:
        require(form.get('attempt_evidence_recipe') == recipe.recipe_id, 'EVIDENCE_SCOPE', 'Explicitly select the recipe these attestations apply to')
    evidence = AttemptEvidence(recipe, (), probability_ref, consumption_ref, None)
    fields = ('tax', 'sale_fee', 'rounding', 'fee_source')
    fees = SaleFees(*(form[key] for key in fields)) if all(form.get(key) for key in fields) else None
    selling = Money(form['selling'], market.currency) if form.get('selling') else None
    result = attempt_economics(recipe, market, observations, (PlannedSale(target.item, target.quantity, selling, fees),),
                              evidence=evidence, fee_override=override, max_scenarios=128)
    names = {item.identity: item.aliases[0].text for item in catalog.items}
    def quantities(entries):
        return escape(', '.join(f'{q.quantity} × {names[q.item]}' for q in entries) or 'None')
    html = '<h2>One-attempt scenarios</h2><p>Replacement cost for one attempt. Expected value is not a guaranteed return; sales are assumptions, and unplanned outputs have no resale credit.</p>'
    for label, value in (('Expected net revenue', result.expected_revenue), ('Expected attempt cost', result.expected_cost),
                         ('Expected profit', result.expected_profit), ('Worst modeled profit', result.worst_profit),
                         ('Best modeled profit', result.best_profit)):
        html += '<p>' + label + ': ' + exact_expected(value, market) + '</p>'
    loss = result.loss_probability
    html += '<p>Modeled probability of loss: ' + ('Unknown' if loss is None else f'{loss.numerator}/{loss.denominator}') + '</p>'
    html += '<table><tr><th>Outcome</th><th>Probability</th><th>Outputs</th><th>Planned sales</th><th>Leftovers</th><th>Net revenue</th><th>Cost</th><th>Profit</th></tr>'
    for s in result.scenarios:
        p = 'Unknown / unverified' if s.probability is None else f'{s.probability.numerator}/{s.probability.denominator}'
        html += f'<tr><td>{s.outcome_index + 1}</td><td>{p}</td><td>{quantities(s.outputs)}</td><td>{quantities(s.sold)}</td><td>{quantities(s.leftovers)}</td><td>{exact_expected(s.revenue, market)}</td><td>{exact_expected(s.cost, market)}</td><td>{exact_expected(s.profit, market)}</td></tr>'
    html += '</table><p>' + escape(', '.join(result.issues)) + '</p><h3>Evidence and sources</h3>'
    for index, outcome in enumerate(recipe.outcomes):
        html += f'<p>Outcome {index + 1}: catalog probability ' + escape(outcome.probability or 'unknown') + ' · source ' + escape(outcome.probability_source or 'unknown') + '</p>'
    html += '<p>Probability attestation: ' + escape(probability_ref or 'None') + '; full-consumption evidence: ' + escape(consumption_ref or 'None') + '</p>'
    for line in result.materials.lines:
        html += '<p>' + escape(names[line.item.item] + ': ' + reference_label(line.observation)) + '</p>'
    return html
