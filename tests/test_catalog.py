from dataclasses import replace
import unittest

from aioncrafter.catalog import CatalogIndex, import_catalog, validate_catalog
from aioncrafter.codec import ValidationError, dumps, loads
from aioncrafter.identity import DatasetKind
from aioncrafter.models import Alias, Catalog, ItemQuantity, Outcome, RightsStatus
from tests.helpers import FIXTURE, catalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.c = catalog()

    def test_fixture_round_trip_and_synthetic_label(self):
        c = import_catalog(dumps(self.c).encode())
        self.assertEqual(c, self.c)
        self.assertEqual(c.scope.dataset_kind, DatasetKind.SYNTHETIC)
        self.assertEqual((len(c.items), len(c.recipes)), (7, 3))

    def test_search_is_localized_accent_insensitive_and_scope_exact(self):
        index = CatalogIndex(self.c)
        self.assertEqual(index.resolve("MINERAL SINTETICO", "es", self.c.scope).identity.item_id, "ore")
        self.assertEqual(index.search("Mineral sintético", "en", self.c.scope), ())
        self.assertEqual(index.search("Synthetic ore", "en", replace(self.c.scope, build="other")), ())

    def test_same_base_item_variants_require_explicit_selection(self):
        index = CatalogIndex(self.c)
        self.assertEqual(len(index.search("Poción sintética", "es", self.c.scope)), 2)
        with self.assertRaisesRegex(ValidationError, "AMBIGUOUS_ALIAS"):
            index.resolve("Poción sintética", "es", self.c.scope)

    def test_alias_collision_across_base_ids_is_rejected(self):
        bad = replace(self.c.items[1], aliases=(Alias("es", "Mineral sintético"),))
        with self.assertRaisesRegex(ValidationError, "AMBIGUOUS_ALIAS"):
            validate_catalog(replace(self.c, items=(self.c.items[0], bad, *self.c.items[2:])))

    def test_orphan_recipe_reference_rejected(self):
        with self.assertRaisesRegex(ValidationError, "ORPHAN_ITEM"):
            validate_catalog(replace(self.c, items=self.c.items[1:]))

    def test_duplicate_identity_rejected(self):
        with self.assertRaisesRegex(ValidationError, "DUPLICATE_ITEM"):
            validate_catalog(replace(self.c, items=(*self.c.items, self.c.items[0])))

    def test_duplicate_recipe_rejected(self):
        with self.assertRaisesRegex(ValidationError, "DUPLICATE_RECIPE"):
            validate_catalog(replace(self.c, recipes=(*self.c.recipes, self.c.recipes[0])))

    def test_multi_recipe_cycle_rejected(self):
        reverse = replace(self.c.recipes[0], recipe_id="reverse", inputs=(ItemQuantity(self.c.items[2].identity, 1),),
                          outcomes=(Outcome((ItemQuantity(self.c.items[0].identity, 1),), "1", "SYNTHETIC"),))
        with self.assertRaisesRegex(ValidationError, "RECIPE_CYCLE"):
            validate_catalog(replace(self.c, recipes=(*self.c.recipes, reverse)))

    def test_self_cycle_rejected(self):
        recipe = replace(self.c.recipes[0], outcomes=(Outcome(self.c.recipes[0].inputs, "1", "SYNTHETIC"),))
        with self.assertRaisesRegex(ValidationError, "RECIPE_CYCLE"):
            validate_catalog(replace(self.c, recipes=(recipe,)))

    def test_scope_and_rights_rejected(self):
        foreign = replace(self.c.items[0], identity=replace(self.c.items[0].identity, scope=replace(self.c.scope, region="OTHER")))
        with self.assertRaisesRegex(ValidationError, "SCOPE_MISMATCH"):
            validate_catalog(replace(self.c, items=(foreign, *self.c.items[1:])))
        # Empty real catalog still cannot pass a rights gate solely with a URL.
        real_scope = replace(self.c.scope, dataset_kind=DatasetKind.GAME)
        source = replace(self.c.provenance, dataset_kind=DatasetKind.GAME, rights_status=RightsStatus.UNVERIFIED)
        with self.assertRaisesRegex(ValidationError, "RIGHTS_UNVERIFIED"):
            validate_catalog(replace(self.c, scope=real_scope, provenance=source))

    def test_unknown_fees_requirements_and_probabilities_preserved(self):
        c = loads(Catalog, dumps(self.c))
        self.assertIsNone(c.recipes[2].fees)
        self.assertIsNone(c.recipes[2].requirements)
        self.assertEqual(c.recipes[1].fees, ())
        self.assertTrue(all(o.probability is None for o in c.recipes[1].outcomes))

    def test_reject_invalid_schema_encoding_size_and_extra_fields(self):
        for payload in [b'\xff', b' ' * (8 * 1024 * 1024 + 1),
                        FIXTURE.read_bytes().replace(b'"schema_version": 1', b'"schema_version": 999'),
                        FIXTURE.read_bytes().replace(b'"schema_version": 1', b'"schema_version": 1, "unexpected": 0')]:
            with self.subTest(prefix=payload[:30]), self.assertRaises(ValidationError):
                import_catalog(payload)
