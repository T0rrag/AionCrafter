from dataclasses import replace
import unittest

from aioncrafter.codec import ValidationError, dumps, loads
from aioncrafter.identity import (CatalogScope, Currency, DatasetKind, FactionMode,
                                ItemIdentity, MarketKind, MarketScope, PriceIdentity, Tradability, Variant)


def example():
    scope = CatalogScope("synthetic-demo", "SYNTHETIC", "test-build-1", DatasetKind.SYNTHETIC)
    item = ItemIdentity(scope, "ore-001", Variant("standard", 0, Tradability.TRADEABLE, ()))
    market = MarketScope(DatasetKind.SYNTHETIC, "SYNTHETIC", MarketKind.SERVER, "test-server",
                         FactionMode.NOT_APPLICABLE, None, Currency("synthetic-demo", "TEST", 2))
    return item, market


class IdentityTests(unittest.TestCase):
    def test_round_trip_is_stable(self):
        item, market = example()
        price = PriceIdentity(item, market)
        self.assertEqual(loads(PriceIdentity, dumps(price)), price)
        self.assertEqual(loads(PriceIdentity, dumps(price)).key, price.key)

    def test_each_sale_dimension_changes_identity(self):
        item, market = example()
        variants = [replace(item.variant, quality="rare"), replace(item.variant, enhancement=1),
                    replace(item.variant, tradability=Tradability.BOUND),
                    replace(item.variant, attributes=(("binding", "account"),))]
        changed_items = [replace(item, variant=v) for v in variants]
        changed_items += [replace(item, item_id="ORE-001"), replace(item, scope=replace(item.scope, build="other")),
                          replace(item, scope=replace(item.scope, namespace="another-source"))]
        keys = [PriceIdentity(x, market).key for x in [item, *changed_items]]
        self.assertEqual(len(set(keys)), len(keys))
        markets = [replace(market, kind=MarketKind.GROUP), replace(market, market_id="another-server"),
                   replace(market, currency=replace(market.currency, code="OTHER")),
                   replace(market, currency=replace(market.currency, decimal_places=0)),
                   replace(market, faction_mode=FactionMode.SPECIFIC, faction_id="team-a")]
        self.assertEqual(len({PriceIdentity(item, m).key for m in [market, *markets]}), 6)

    def test_unknown_scope_cannot_be_priced(self):
        item, market = example()
        for m in [replace(market, region=None), replace(market, currency=None),
                  replace(market, faction_mode=FactionMode.UNKNOWN),
                  replace(market, kind=MarketKind.UNKNOWN, market_id=None)]:
            with self.subTest(m=m), self.assertRaisesRegex(ValidationError, "UNRESOLVED_SCOPE"):
                PriceIdentity(item, m)
        for v in [replace(item.variant, quality=None), replace(item.variant, enhancement=None),
                  replace(item.variant, tradability=Tradability.UNKNOWN)]:
            with self.assertRaisesRegex(ValidationError, "UNRESOLVED_SCOPE"):
                PriceIdentity(replace(item, variant=v), market)

    def test_cross_region_and_synthetic_real_joins_rejected(self):
        item, market = example()
        for m in [replace(market, region="other"), replace(market, dataset_kind=DatasetKind.GAME)]:
            with self.assertRaisesRegex(ValidationError, "SCOPE_MISMATCH"):
                PriceIdentity(item, m)

    def test_attribute_order_is_canonical_and_duplicates_rejected(self):
        a = Variant("x", 0, Tradability.BOUND, (("b", "2"), ("a", "1")))
        b = Variant("x", 0, Tradability.BOUND, (("a", "1"), ("b", "2")))
        self.assertEqual(dumps(a), dumps(b))
        with self.assertRaisesRegex(ValidationError, "DUPLICATE_ATTRIBUTE"):
            replace(a, attributes=(("a", "1"), ("a", "2")))

    def test_delimiters_and_unicode_do_not_collide(self):
        item, _ = example()
        a = replace(item, item_id='a/b:"é"')
        b = replace(item, item_id='a/b:"e"')
        self.assertNotEqual(a.key, b.key)
        self.assertEqual(loads(ItemIdentity, dumps(a)), a)

    def test_invalid_direct_values_rejected(self):
        item, market = example()
        for enhancement in [True, -1, 0.0, "0"]:
            with self.subTest(value=enhancement), self.assertRaises(ValidationError):
                replace(item.variant, enhancement=enhancement)
        for value in ["", " abc", "a\nb"]:
            with self.assertRaises(ValidationError):
                replace(item, item_id=value)
        with self.assertRaises(ValidationError):
            replace(market, faction_id="unexpected")

    def test_json_is_strict(self):
        item, _ = example()
        text = dumps(item)
        for bad in [text.replace('"enhancement":0', '"enhancement":false'),
                    text.replace('"enhancement":0', '"enhancement":NaN'),
                    text.replace('"item_id":"ore-001"', '"item_id":"ore-001","item_id":"other"'),
                    text.replace('"item_id":"ore-001"', '"item_id":"ore-001","typo":1')]:
            with self.assertRaises(ValidationError):
                loads(ItemIdentity, bad)
