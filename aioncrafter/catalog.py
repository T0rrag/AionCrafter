"""Validation before publication. No provider access or implicit alias selection."""
from collections import deque

from .codec import ValidationError, loads, require
from .identity import CatalogScope, DatasetKind, normalize_alias
from .models import Catalog, Item, RightsStatus

MAX_IMPORT_BYTES = 8 * 1024 * 1024


def validate_catalog(catalog: Catalog) -> None:
    require(bool(catalog.items), "EMPTY_CATALOG", "Catalog must contain items")
    require(catalog.provenance.dataset_kind is catalog.scope.dataset_kind, "PROVENANCE", "Catalog and source dataset differ")
    require(catalog.provenance.rights_status in (RightsStatus.SYNTHETIC, RightsStatus.PERMITTED),
            "RIGHTS_UNVERIFIED", "A permitted source and rights reference are required")
    items: dict[str, Item] = {}
    aliases: dict[tuple[str, str], str] = {}
    for item in catalog.items:
        require(item.identity.scope == catalog.scope, "SCOPE_MISMATCH", "Item belongs to a different catalog scope")
        require(item.identity.key not in items, "DUPLICATE_ITEM", item.identity.item_id)
        items[item.identity.key] = item
        for alias in item.aliases:
            key = (alias.language.casefold(), normalize_alias(alias.text))
            prior = aliases.get(key)
            require(prior is None or prior == item.identity.item_id, "AMBIGUOUS_ALIAS", f"{alias.text} maps to different base item IDs")
            aliases[key] = item.identity.item_id
    recipe_ids = set()
    edges = {key: set() for key in items}
    for recipe in catalog.recipes:
        require(recipe.scope == catalog.scope, "SCOPE_MISMATCH", "Recipe belongs to a different build/region")
        require(recipe.provenance.rights_status in (RightsStatus.SYNTHETIC, RightsStatus.PERMITTED), "RIGHTS_UNVERIFIED", recipe.recipe_id)
        require(recipe.recipe_id not in recipe_ids, "DUPLICATE_RECIPE", recipe.recipe_id)
        recipe_ids.add(recipe.recipe_id)
        outputs = [q for outcome in recipe.outcomes for q in outcome.outputs]
        for q in [*recipe.inputs, *outputs]:
            require(q.item.key in items, "ORPHAN_ITEM", f"{recipe.recipe_id}: {q.item.item_id}")
        for source in recipe.inputs:
            edges[source.item.key].update(q.item.key for q in outputs)
    # Kahn's algorithm avoids recursion failures on long imported crafting chains.
    incoming = dict.fromkeys(edges, 0)
    for targets in edges.values():
        for target in targets:
            incoming[target] += 1
    queue = deque(key for key, degree in incoming.items() if degree == 0)
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for target in edges[node]:
            incoming[target] -= 1
            if incoming[target] == 0:
                queue.append(target)
    require(visited == len(edges), "RECIPE_CYCLE", "Crafting graph contains a cycle")


def import_catalog(payload: bytes) -> Catalog:
    require(type(payload) is bytes and len(payload) <= MAX_IMPORT_BYTES, "IMPORT_SIZE", "Catalog must be UTF-8 bytes, at most 8 MiB")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError("ENCODING", "Catalog must be UTF-8") from exc
    catalog = loads(Catalog, text)
    validate_catalog(catalog)
    return catalog


class CatalogIndex:
    def __init__(self, catalog: Catalog):
        validate_catalog(catalog)
        self.catalog = catalog

    def search(self, alias: str, language: str, scope: CatalogScope) -> tuple[Item, ...]:
        if scope != self.catalog.scope:
            return ()
        query = normalize_alias(alias)
        return tuple(item for item in self.catalog.items
                     if any(a.language.casefold() == language.casefold() and normalize_alias(a.text) == query for a in item.aliases))

    def resolve(self, alias: str, language: str, scope: CatalogScope) -> Item:
        matches = self.search(alias, language, scope)
        require(bool(matches), "ITEM_NOT_FOUND", alias)
        require(len(matches) == 1, "AMBIGUOUS_ALIAS", "Choose an explicit item variant")
        return matches[0]
