"""Pure deterministic recipe expansion; explicit routes, no prices or game access."""
from dataclasses import dataclass
from fractions import Fraction
from heapq import heapify, heappop, heappush

from .catalog import validate_catalog
from .codec import require
from .identity import ItemIdentity
from .models import Catalog, ItemQuantity, Recipe
from .valuation import InventoryEntry


@dataclass(frozen=True)
class CraftStep:
    recipe: Recipe
    crafts: int
    inputs: tuple[ItemQuantity, ...]
    outputs: tuple[ItemQuantity, ...]


@dataclass(frozen=True)
class BatchLine:
    item: ItemIdentity
    required: int
    produced: int
    owned_used: int
    external: int
    leftover: int


@dataclass(frozen=True)
class BatchPlan:
    requested: tuple[ItemQuantity, ...]
    # Execution order: inputs before consumers. Every recipe executes at most once
    # as an aggregated group of crafts, not once per path through the recipe graph.
    steps: tuple[CraftStep, ...]
    lines: tuple[BatchLine, ...]
    materials: tuple[ItemQuantity, ...]
    leftovers: tuple[ItemQuantity, ...]
    inventory_remaining: tuple[InventoryEntry, ...]
    issues: tuple[str, ...]


def plan_batches(catalog: Catalog, requested: tuple[ItemQuantity, ...],
                 recipe_ids: tuple[str, ...], *, inventory: tuple[InventoryEntry, ...] = (),
                 max_recipes: int = 10000) -> BatchPlan:
    """Expand one explicit route; items without a selected producer are external.

    Selected recipes must have known deterministic outcomes and nonoverlapping outputs.
    This supports joint outputs but does not silently choose between competing recipes.
    Recipe requirements are reported for manual confirmation, never assumed satisfied.
    max_recipes is a computational guard, not a claimed game limit.
    """
    require(type(catalog) is Catalog, 'TYPE', 'Expected a catalog')
    validate_catalog(catalog)
    require(type(requested) is tuple and bool(requested) and all(type(q) is ItemQuantity for q in requested),
            'QUANTITY', 'Select at least one requested item')
    require(type(recipe_ids) is tuple and all(type(r) is str for r in recipe_ids), 'TYPE', 'Recipe choices must be a tuple of IDs')
    require(len(set(recipe_ids)) == len(recipe_ids), 'DUPLICATE_RECIPE', 'Select each recipe once')
    require(type(max_recipes) is int and max_recipes > 0 and len(recipe_ids) <= max_recipes,
            'PLANNING_LIMIT', 'Selected recipes exceed the explicit planning limit')
    require(type(inventory) is tuple and all(type(i) is InventoryEntry for i in inventory), 'TYPE', 'Expected inventory tuple')
    items = {i.identity: i for i in catalog.items}
    recipes = {r.recipe_id: r for r in catalog.recipes}
    demand, owned = {}, {}
    for q in requested:
        require(q.item in items, 'ORPHAN_ITEM', 'Requested item/variant is outside the catalog')
        demand[q.item] = demand.get(q.item, 0) + q.quantity
    targets = tuple(ItemQuantity(i, q) for i, q in sorted(demand.items(), key=lambda x: x[0].key))
    for entry in inventory:
        require(entry.item in items, 'ORPHAN_ITEM', 'Inventory item/variant is outside the catalog')
        require(entry.item not in owned, 'DUPLICATE_INVENTORY', 'Combine inventory quantities by item')
        owned[entry.item] = entry.quantity
    producer, selected = {}, {}
    for recipe_id in recipe_ids:
        require(recipe_id in recipes, 'RECIPE', 'Selected recipe is not in the catalog')
        recipe = recipes[recipe_id]
        require(len(recipe.outcomes) == 1 and recipe.outcomes[0].probability is not None
                and Fraction(recipe.outcomes[0].probability) == 1,
                'NONDETERMINISTIC', 'Recursive batches require a known guaranteed outcome')
        selected[recipe_id] = recipe
        for output in recipe.outcomes[0].outputs:
            require(output.item not in producer, 'AMBIGUOUS_PRODUCER', 'Selected recipes produce the same variant; choose one route')
            producer[output.item] = recipe_id
    # Discover selected dependencies iteratively so a deep valid chain cannot overflow
    # Python's recursion stack. Catalog validation already rejects all recipe cycles.
    frontier = [producer[i] for i in demand if i in producer]
    edges = {}
    while frontier:
        recipe_id = frontier.pop()
        if recipe_id in edges:
            continue
        dependencies = {producer[q.item] for q in selected[recipe_id].inputs if q.item in producer}
        edges[recipe_id] = dependencies
        frontier.extend(dependencies)
    incoming = dict.fromkeys(edges, 0)
    for deps in edges.values():
        for dep in deps:
            incoming[dep] += 1
    ready = [r for r, count in incoming.items() if count == 0]
    heapify(ready)
    steps, produced, issues = [], {}, []
    visited = 0
    while ready:
        recipe_id = heappop(ready)
        visited += 1
        recipe = selected[recipe_id]
        outputs = recipe.outcomes[0].outputs
        # Every consumer's demand has arrived before the shared producer is rounded.
        crafts = max((max(0, demand.get(q.item, 0) - owned.get(q.item, 0)) + q.quantity - 1) // q.quantity
                     for q in outputs)
        if crafts:
            inputs = tuple(ItemQuantity(q.item, q.quantity * crafts) for q in recipe.inputs)
            made = tuple(ItemQuantity(q.item, q.quantity * crafts) for q in outputs)
            for q in inputs:
                demand[q.item] = demand.get(q.item, 0) + q.quantity
            for q in made:
                produced[q.item] = q.quantity
            steps.append(CraftStep(recipe, crafts, inputs, made))
            if recipe.requirements is None:
                issues.append(f'unknown_requirements:{recipe_id}')
            elif recipe.requirements:
                issues.append(f'confirm_requirements:{recipe_id}')
        for dep in sorted(edges[recipe_id]):
            incoming[dep] -= 1
            if incoming[dep] == 0:
                heappush(ready, dep)
    require(visited == len(edges), 'RECIPE_CYCLE', 'Selected recipe graph contains a cycle')
    lines = []
    remaining = dict(owned)
    for item in sorted(demand.keys() | produced.keys(), key=lambda i: i.key):
        required, made = demand.get(item, 0), produced.get(item, 0)
        # A joint output can make earlier inventory unnecessary; prefer generated
        # material and retain unused owned stock instead of double-counting it.
        used = min(owned.get(item, 0), max(0, required - made))
        if item in remaining:
            remaining[item] -= used
        lines.append(BatchLine(item, required, made, used, max(0, required - made - used), max(0, made - required)))
    return BatchPlan(targets, tuple(reversed(steps)), tuple(lines),
                     tuple(ItemQuantity(x.item, x.external) for x in lines if x.external),
                     tuple(ItemQuantity(x.item, x.leftover) for x in lines if x.leftover),
                     tuple(InventoryEntry(i, n) for i, n in sorted(remaining.items(), key=lambda x: x[0].key)),
                     tuple(sorted(issues)))
