from dataclasses import replace
import unittest

from aioncrafter.batches import plan_batches
from aioncrafter.codec import ValidationError
from aioncrafter.models import ItemQuantity
from aioncrafter.valuation import InventoryEntry
from .synthetic_crafting import graph


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.catalog, self.items = graph((
            ('ingot', {'ore': 3}, {'ingot': 4}),
            ('left', {'ingot': 2}, {'left': 1}),
            ('right', {'ingot': 2}, {'right': 1}),
            ('final', {'left': 1, 'right': 1}, {'final': 1})))

    def plan(self, targets=None, recipes=None, **kwargs):
        targets = targets or {'final': 1}
        return plan_batches(self.catalog, tuple(ItemQuantity(self.items[k], v) for k, v in targets.items()),
                            tuple(r.recipe_id for r in self.catalog.recipes) if recipes is None else recipes, **kwargs)

    def test_shared_diamond_rounds_only_after_aggregation(self):
        plan = self.plan()
        self.assertEqual({q.item.item_id: q.quantity for q in plan.materials}, {'ore': 3})
        self.assertEqual({s.recipe.recipe_id: s.crafts for s in plan.steps}, {'ingot': 1, 'left': 1, 'right': 1, 'final': 1})
        order = [s.recipe.recipe_id for s in plan.steps]
        self.assertLess(order.index('ingot'), order.index('left'))
        self.assertLess(order.index('right'), order.index('final'))

    def test_shared_root_and_nested_demands_combine(self):
        plan = self.plan({'final': 1, 'ingot': 1})
        self.assertEqual(plan.materials[0].quantity, 6)
        self.assertEqual([(x.item.item_id, x.quantity) for x in plan.leftovers], [('ingot', 3)])

    def test_duplicate_targets_merge_and_route_order_is_irrelevant(self):
        ids = tuple(r.recipe_id for r in self.catalog.recipes)
        requested = (ItemQuantity(self.items['final'], 1),) * 2
        one = plan_batches(self.catalog, requested, ids)
        self.assertEqual(one, plan_batches(self.catalog, tuple(reversed(requested)), tuple(reversed(ids))))
        self.assertEqual(one.requested, (ItemQuantity(self.items['final'], 2),))

    def test_unselected_intermediate_stays_external(self):
        plan = self.plan(recipes=('final',))
        self.assertEqual({q.item.item_id: q.quantity for q in plan.materials}, {'left': 1, 'right': 1})
        self.assertEqual(self.plan(recipes=()).steps, ())

    def test_inventory_is_used_once_after_shared_demand(self):
        plan = self.plan(inventory=(InventoryEntry(self.items['ingot'], 1), InventoryEntry(self.items['ore'], 2)))
        self.assertEqual([(x.item.item_id, x.quantity) for x in plan.materials], [('ore', 1)])
        # A full four-unit ingot batch covers demand, leaving the owned ingot untouched.
        self.assertEqual({x.item.item_id: x.quantity for x in plan.inventory_remaining}, {'ingot': 1, 'ore': 0})
        for line in plan.lines:
            self.assertEqual(line.produced + line.owned_used + line.external, line.required + line.leftover)

    def test_inventory_can_avoid_whole_subtree(self):
        plan = self.plan(inventory=(InventoryEntry(self.items['final'], 1),))
        self.assertEqual((plan.steps, plan.materials, plan.leftovers), ((), (), ()))
        self.assertEqual(plan.lines[0].owned_used, 1)

    def test_joint_outputs_share_one_recipe_and_inventory_is_not_double_counted(self):
        c, i = graph((('joint', {'ore': 3}, {'a': 2, 'b': 3}),))
        plan = plan_batches(c, (ItemQuantity(i['a'], 3), ItemQuantity(i['b'], 4)), ('joint',),
                            inventory=(InventoryEntry(i['a'], 2),))
        self.assertEqual(plan.steps[0].crafts, 2)
        self.assertEqual({q.item.item_id: q.quantity for q in plan.leftovers}, {'a': 1, 'b': 2})
        self.assertEqual(plan.inventory_remaining[0].quantity, 2)

    def test_joint_output_can_supply_a_separate_consumer(self):
        c, i = graph((('joint', {'ore': 1}, {'a': 2, 'b': 3}), ('final', {'b': 5}, {'final': 1})))
        plan = plan_batches(c, (ItemQuantity(i['a'], 1), ItemQuantity(i['final'], 1)), ('joint', 'final'))
        self.assertEqual([(s.recipe.recipe_id, s.crafts) for s in plan.steps], [('joint', 2), ('final', 1)])
        self.assertEqual({q.item.item_id: q.quantity for q in plan.leftovers}, {'a': 3, 'b': 1})

    def test_competing_producers_require_an_explicit_nonoverlapping_route(self):
        c, i = graph((('one', {'ore': 1}, {'a': 1}), ('two', {'ore': 2}, {'a': 3})))
        with self.assertRaisesRegex(ValidationError, 'AMBIGUOUS_PRODUCER'):
            plan_batches(c, (ItemQuantity(i['a'], 1),), ('one', 'two'))
        self.assertEqual(plan_batches(c, (ItemQuantity(i['a'], 1),), ('two',)).leftovers[0].quantity, 2)

    def test_unknown_or_stochastic_outcomes_not_treated_as_guaranteed(self):
        c, i = graph((('one', {'ore': 1}, {'a': 1}),))
        outcome = replace(c.recipes[0].outcomes[0], probability=None, probability_source=None)
        c = replace(c, recipes=(replace(c.recipes[0], outcomes=(outcome,)),))
        with self.assertRaisesRegex(ValidationError, 'NONDETERMINISTIC'):
            plan_batches(c, (ItemQuantity(i['a'], 1),), ('one',))

    def test_cycles_fail_before_expansion(self):
        c, i = graph((('ab', {'a': 1}, {'b': 1}), ('ba', {'b': 1}, {'a': 1})))
        with self.assertRaisesRegex(ValidationError, 'RECIPE_CYCLE'):
            plan_batches(c, (ItemQuantity(i['a'], 1),), ('ab', 'ba'))

    def test_requirements_are_preserved_for_confirmation(self):
        self.catalog = replace(self.catalog, recipes=tuple(replace(r, requirements=None if r.recipe_id == 'final' else ('SYNTHETIC skill',)) for r in self.catalog.recipes))
        self.assertIn('unknown_requirements:final', self.plan().issues)
        self.assertIn('confirm_requirements:ingot', self.plan().issues)

    def test_foreign_variant_inventory_and_invalid_choices_fail(self):
        foreign = replace(self.items['final'], variant=replace(self.items['final'].variant, enhancement=42))
        for args in ({'recipe_ids': ('missing',)}, {'recipe_ids': ('final', 'final')},
                     {'recipe_ids': ('final',), 'inventory': (InventoryEntry(foreign, 1),)},
                     {'recipe_ids': ('final',), 'max_recipes': True}):
            with self.subTest(args=args), self.assertRaises(ValidationError):
                plan_batches(self.catalog, (ItemQuantity(self.items['final'], 1),), **args)

    def test_unreachable_recipe_is_not_executed(self):
        plan = self.plan({'ore': 1})
        self.assertEqual(plan.steps, ())
        self.assertEqual(plan.materials, (ItemQuantity(self.items['ore'], 1),))

    def test_long_chain_uses_iterative_expansion(self):
        c, i = graph(tuple((f'r{n}', {f'i{n}': 1}, {f'i{n+1}': 1}) for n in range(1050)))
        plan = plan_batches(c, (ItemQuantity(i['i1050'], 2),), tuple(r.recipe_id for r in c.recipes))
        self.assertEqual(len(plan.steps), 1050)
        self.assertEqual(plan.materials, (ItemQuantity(i['i0'], 2),))
