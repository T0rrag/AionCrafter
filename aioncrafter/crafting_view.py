"""Offline recursive planning presentation; no automatic prices or source requests."""
from html import escape

from .batches import plan_batches
from .buycraft import compare_routes, price_plan
from .codec import require
from .economics import amount
from .models import CraftFee, FeeBasis, ItemQuantity, Money
from .references import reference_label
from .stochastic_view import render_scenarios, scenario_controls
from .ranking_view import render_ranking, ranking_controls


def crafting_controls(catalog, form):
    def select(name, label, choices, default):
        return '<label>' + label + f'<select name="{name}">' + ''.join(
            f'<option value="{key}" {"selected" if form.get(name, default) == key else ""}>{text}</option>'
            for key, text in choices) + '</select></label>'
    html = '<fieldset><legend>Recursive crafting (crafting workflow only)</legend>'
    html += select('plan_mode', 'Planning mode', (('selected', 'Expand selected recipes'), ('compare', 'Compare buying and crafting'), ('scenarios', 'One-attempt outcome scenarios'), ('rank', 'Rank conditional craft routes')), 'selected')
    html += select('plan_objective', 'Cost view', (('additional_cash', 'Additional cash after owned stock'),
                                                ('replacement_cost', 'Replacement cost without stock deduction')), 'additional_cash')
    html += '<p>The product and recipe selected above define the target. Choose intermediate recipes below; unselected intermediates stay external purchases. The target recipe is always included as a candidate. All requirements still need manual confirmation.</p>'
    names = {item.identity: item.aliases[0].text for item in catalog.items}
    for index, recipe in enumerate(catalog.recipes):
        outputs = ', '.join(names[q.item] for outcome in recipe.outcomes for q in outcome.outputs)
        html += select(f'use_recipe{index}', escape(recipe.recipe_id + ' — ' + outputs),
                       (('no', 'Do not expand'), ('yes', 'Use as a crafting candidate')), 'no')
    return html + '<p>Comparison supports up to 7 candidate recipes. It tests whole craft-or-buy routes, not every possible mixture. The crafting-fee override above applies only to the selected target recipe; other recipes retain their recorded fees or remain unknown.</p></fieldset>' + scenario_controls(catalog, form) + ranking_controls(catalog, form)


def render_crafting(catalog, form, market, observations, inventory):
    names = {item.identity: item.aliases[0].text for item in catalog.items}
    recipe = next((r for r in catalog.recipes if r.recipe_id == form.get('recipe')), None)
    require(recipe is not None, 'RECIPE', 'Select the target recipe')
    index = int(form.get('product', ''))
    require(0 <= index < len(catalog.items), 'OUTPUT', 'Choose a product')
    target = ItemQuantity(catalog.items[index].identity, int(form.get('target', '')))
    require(any(q.item == target.item for outcome in recipe.outcomes for q in outcome.outputs), 'OUTPUT', 'Recipe must produce the selected product')
    objective = form.get('plan_objective', 'additional_cash')
    mode = form.get('plan_mode', 'selected')
    require(objective in ('additional_cash', 'replacement_cost') and mode in ('selected', 'compare', 'scenarios', 'rank'),
            'PLAN_MODE', 'Select a supported planning mode and cost view')
    selected = {recipe.recipe_id}
    for i, candidate in enumerate(catalog.recipes):
        flag = form.get(f'use_recipe{i}', 'no')
        require(flag in ('yes', 'no'), 'PLAN_MODE', 'Choose whether to expand each recipe')
        if flag == 'yes':
            selected.add(candidate.recipe_id)
    chosen = tuple(sorted(selected))
    overrides = {}
    if form.get('craft_fee'):
        overrides[recipe.recipe_id] = (CraftFee(Money(form['craft_fee'], market.currency), FeeBasis(form.get('craft_basis', ''))),)
    if mode == 'scenarios':
        return render_scenarios(catalog, form, recipe, target, market, observations, overrides.get(recipe.recipe_id))
    if mode == 'rank':
        return render_ranking(catalog, form, target, chosen, market, observations, inventory, overrides)
    html = '<h2>Recursive crafting estimate</h2><p>' + ('Additional cash after owned stock' if objective == 'additional_cash'
                                                    else 'Replacement cost without stock deduction') + '</p>'
    if mode == 'compare':
        require(len(chosen) <= 7, 'PLANNING_LIMIT', 'Choose at most 7 candidate recipes for comparison')
        result = compare_routes(catalog, (target,), chosen, market, observations, objective=objective,
                                inventory=inventory, fee_overrides=overrides, max_routes=128)
        html += f'<p>{len(result.routes)} route choices evaluated; {result.unresolved_routes} have unknown costs. Lowest known estimates are conditional comparisons, not recommendations or guaranteed stock. Whole craft-or-buy routes only; no mixed purchase/craft of the same variant.</p>'
        html += '<table><tr><th>Crafting candidates</th><th>Estimated cost</th><th>Uncertainty</th></tr>'
        ordered = sorted(result.routes, key=lambda r: (r.cost.total is None, r.cost.total or 0, r.selected_recipes))
        for route in ordered[:20]:
            html += '<tr><td>' + escape(', '.join(route.selected_recipes) or 'Buy all requested items') + '</td><td>'
            html += ('Unknown' if route.cost.total is None else amount(route.cost.total, market)) + '</td><td>' + escape(', '.join(route.cost.issues)) + '</td></tr>'
        html += '</table>'
        if len(ordered) > 20:
            html += '<p>Showing the 20 lowest known or unresolved choices. Use selected-recipe expansion to inspect a specific route.</p>'
        cost = result.lowest_known[0].cost if result.lowest_known else ordered[0].cost
        html += '<h3>Example route details</h3><p>' + ('One lowest known route is detailed below.' if result.lowest_known
                                                      else 'No fully priced route; the first unresolved route is detailed below.') + '</p>'
    else:
        plan = plan_batches(catalog, (target,), chosen, inventory=inventory if objective == 'additional_cash' else ())
        used = {s.recipe.recipe_id for s in plan.steps}
        cost = price_plan(plan, market, observations, fee_overrides={r: f for r, f in overrides.items() if r in used})
    html += '<p>Total acquisition and crafting cost: ' + ('Unknown' if cost.total is None else amount(cost.total, market))
    html += '; crafting fees: ' + ('Unknown' if cost.crafting_fees is None else amount(cost.crafting_fees, market)) + '</p>'
    html += '<table><tr><th>Execution order</th><th>Crafts</th><th>Requirements</th></tr>'
    for step in cost.plan.steps:
        requirements = 'Unknown — check manually' if step.recipe.requirements is None else ', '.join(step.recipe.requirements) or 'No requirements recorded'
        html += f'<tr><td>{escape(step.recipe.recipe_id)}</td><td>{step.crafts}</td><td>{escape(requirements)}</td></tr>'
    html += '</table><table><tr><th>Item</th><th>Required</th><th>Crafted</th><th>Owned used</th><th>External</th><th>Leftover</th></tr>'
    for line in cost.plan.lines:
        html += f'<tr><td>{escape(names[line.item])}</td><td>{line.required}</td><td>{line.produced}</td><td>{line.owned_used}</td><td>{line.external}</td><td>{line.leftover}</td></tr>'
    html += '</table><h3>External price sources</h3>'
    for acquisition in cost.acquisitions:
        html += '<p>' + escape(names[acquisition.identity.item]) + ': ' + escape(acquisition.state) + ' · stock unverified</p>'
        for obs in acquisition.observations:
            html += '<p>' + escape(reference_label(obs)) + '</p>'
    html += '<p>' + escape(', '.join(cost.issues)) + '</p>'
    html += '<p>All displayed prices are manual or approved offline references. Quantities and stock remain unverified. Leftovers have no resale credit. Owned inputs are excluded only from the additional-cash view; they are not economically free. This cost plan does not estimate sale proceeds, liquidity or realized profit.</p>'
    return html
