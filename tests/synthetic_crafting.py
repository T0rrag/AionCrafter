"""SYNTHETIC ONLY: fictional recursive graphs; no AION 2 recipes or rules."""
from dataclasses import replace

from aioncrafter.models import Alias, ItemQuantity, Outcome, Recipe
from .helpers import catalog


def graph(specs):
    """Specs are (recipe ID, {input: quantity}, {output: quantity})."""
    base = catalog()
    names = sorted({name for _, ins, outs in specs for name in (*ins, *outs)})
    items = {name: replace(base.items[0], identity=replace(base.items[0].identity, item_id=name),
                          aliases=(Alias('en', 'SYNTHETIC ' + name),)) for name in names}
    identities = {name: item.identity for name, item in items.items()}
    def quantities(values):
        return tuple(ItemQuantity(identities[name], count) for name, count in values.items())
    recipes = tuple(Recipe(name, base.scope, quantities(ins),
                           (Outcome(quantities(outs), '1', 'SYNTHETIC deterministic fixture'),),
                           (), (), base.provenance) for name, ins, outs in specs)
    return replace(base, release_id='SYNTHETIC-recursive', items=tuple(items.values()), recipes=recipes), identities
