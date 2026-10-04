"""End-to-end local HTTP forms; does not claim browser rendering acceptance."""
from dataclasses import replace
from http.server import HTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import tempfile
import unittest
import json

from aioncrafter.codec import dumps, loads
from aioncrafter.models import PriceObservation, PriceType
from aioncrafter.plans import PlanStore, decode_plan
from aioncrafter.web import handler
from tests.helpers import catalog, observation
from tests.http_form import FormControls


class FormAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.c = catalog()
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = str(Path(temp.name) / 'plans.sqlite3')
        Handler = handler(self.c, self.path)
        Handler.log_message = lambda *_: None
        self.server = HTTPServer(('127.0.0.1', 0), Handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        with urlopen(self.url) as response:
            self.form = FormControls(response.read().decode()).fields
        self.form.update(market='test-server', currency='TEST', observed='2026-10-01T10:00:00Z', q0='3', p0='12.30')

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def post(self, form, **changes):
        with urlopen(Request(self.url, data=urlencode(dict(form, **changes)).encode())) as response:
            return response.read().decode()

    def observations(self, form):
        return loads(tuple[PriceObservation, ...], form['reference_payload'])

    def test_calculate_then_search_save_and_reload_preserves_exact_observations(self):
        html = self.post(self.form)
        self.assertIn('Total: 36.90', html)
        self.assertNotIn('role="alert"', html)
        calculated = FormControls(html).fields
        original = self.observations(calculated)
        again = FormControls(self.post(calculated)).fields
        self.assertEqual(self.observations(again), original)
        searched = FormControls(self.post(again, action='search', product_search='pocion')).fields
        self.assertEqual(self.observations(searched), original)
        saved = self.post(searched, action='save', plan_name='SYNTHETIC full form')
        self.assertIn('Saved locally at revision 1', saved)
        loaded = self.post(FormControls(saved).fields, action='load')
        self.assertEqual(self.observations(FormControls(loaded).fields), original)

    def test_mixed_unknown_age_references_manual_edit_and_csv_copy(self):
        first = replace(observation(), price_type=PriceType.SNAPSHOT, observed_at=None)
        second = replace(observation(), observation_id='vendor-2',
                         identity=replace(first.identity, item=self.c.items[1].identity),
                         price_type=PriceType.VENDOR_PURCHASE, unit_price='2',
                         observed_at='2026-09-20T10:00:00Z')
        preview = self.post(self.form, action='references', reference_data=dumps((first, second)))
        self.assertIn('Reference import validated', preview)
        self.assertIn('Snapshot · age unknown', preview)
        self.assertIn('Vendor purchase · age', preview)
        form = FormControls(preview).fields
        calculated = self.post(form)
        self.assertNotIn('role="alert"', calculated)
        form = FormControls(calculated).fields
        self.assertEqual(self.observations(form)[:2], (first, second))
        edited = self.post(form, p0='15', t0='2026-10-02T10:00:00Z')
        self.assertIn('Total: 45.00', edited)
        form = FormControls(edited).fields
        new = self.observations(form)[0]
        self.assertEqual(new.price_type, PriceType.MANUAL)
        self.assertEqual(new.supersedes_id, first.observation_id)
        saved = self.post(form, action='save', plan_name='mixed')
        csv = self.post(FormControls(saved).fields, action='export_csv')
        exported = decode_plan(csv.encode(), self.c, 'csv')
        self.assertEqual(exported.observations[0], new)
        copied = self.post(FormControls(saved).fields, action='import', import_data=csv, import_format='csv')
        copied = self.post(FormControls(copied).fields, action='save', plan_name='mixed copy')
        self.assertIn('Saved locally at revision 1', copied)
        with PlanStore(self.path) as store:
            self.assertEqual(store.load('mixed copy', self.c)[1].observations, exported.observations)

    def test_materials_owned_missing_and_item_batch_workflows_from_real_controls(self):
        html = self.post(self.form, p0='', owned0='3')
        self.assertIn('Total: Incomplete', html)
        self.assertIn('Additional cash required: 0.00', html)
        html = self.post(self.form, workflow='item', product='2', recipe='synthetic-bar', target='3',
                         p0='10', p1='2', selling='30', craft_fee='1', tax='0.1', sale_fee='0',
                         fee_source='SYNTHETIC unverified assumption')
        self.assertNotIn('role="alert"', html)
        self.assertIn('2 crafts · 4 produced · 3 planned sales · 1 unsold leftovers', html)
        self.assertIn('Recorded consumed-material cost: Incomplete', html)
        saved = self.post(FormControls(html).fields, action='save', plan_name='item batch')
        self.assertIn('Saved locally at revision 1', saved)

    def test_reference_id_collision_rejected_without_corrupting_current_form(self):
        form = FormControls(self.post(self.form)).fields
        before = self.observations(form)
        colliding = replace(before[0], observation_id=before[1].observation_id, price_type=PriceType.SNAPSHOT)
        html = self.post(form, action='references', reference_data=dumps((colliding,)))
        self.assertIn('REFERENCE_ID', html)
        self.assertNotIn('Reference import validated', html)
        self.assertEqual(self.observations(FormControls(html).fields), before)

    def test_recursive_plan_roundtrip_from_actual_form_controls(self):
        html = self.post(self.form, workflow='crafting', product='2', recipe='synthetic-bar', target='3',
                         p0='10', p1='2', craft_fee='1', plan_mode='selected', plan_objective='additional_cash')
        self.assertNotIn('role="alert"', html)
        self.assertIn('Recursive crafting estimate', html)
        self.assertIn('<th>Leftover</th>', html)
        self.assertIn('stock unverified', html)
        saved = self.post(FormControls(html).fields, action='save', plan_name='recursive')
        self.assertIn('Saved locally at revision 1', saved)
        loaded = self.post(FormControls(saved).fields, action='load')
        self.assertNotIn('role="alert"', loaded)
        fields = FormControls(loaded).fields
        self.assertEqual(fields['workflow'], 'crafting')
        self.assertEqual(fields['plan_mode'], 'selected')
        self.assertEqual(fields['target'], '3')
        self.assertEqual(self.observations(fields), self.observations(FormControls(saved).fields))

    def test_recursive_comparison_keeps_missing_prices_and_unknown_stock_explicit(self):
        html = self.post(self.form, workflow='crafting', product='2', recipe='synthetic-bar', target='3',
                         p0='', p1='', p2='', craft_fee='0', plan_mode='compare')
        self.assertNotIn('role="alert"', html)
        self.assertIn('2 route choices evaluated; 2 have unknown costs', html)
        self.assertIn('Total acquisition and crafting cost: Unknown', html)
        self.assertIn('no mixed purchase/craft', html)

    def test_recursive_invalid_candidate_cannot_be_saved(self):
        html = self.post(self.form, action='save', plan_name='invalid recursive', workflow='crafting',
                         product='2', recipe='synthetic-bar', target='3', use_recipe0='invalid')
        self.assertIn('PLAN_MODE', html)
        self.assertNotIn('Saved locally at revision', html)
        with PlanStore(self.path) as store:
            self.assertEqual(store.list(), ())

    def test_scenario_view_keeps_unknown_probabilities_and_survives_save_load(self):
        recipe = self.c.recipes[1]
        product = next(i for i, item in enumerate(self.c.items) if item.identity == recipe.outcomes[0].outputs[0].item)
        html = self.post(self.form, workflow='crafting', plan_mode='scenarios', recipe=recipe.recipe_id,
                         product=str(product), target='1', selling='10', tax='0.1', sale_fee='0',
                         fee_source='SYNTHETIC assumption', attempt_evidence_recipe=recipe.recipe_id,
                         consumption_evidence='SYNTHETIC full-input test rule')
        self.assertNotIn('role="alert"', html)
        self.assertIn('Expected profit: Unknown', html)
        self.assertIn('unknown_probabilities', html)
        saved = self.post(FormControls(html).fields, action='save', plan_name='scenario')
        self.assertIn('Saved locally at revision 1', saved)
        loaded = self.post(FormControls(saved).fields, action='load')
        self.assertEqual(FormControls(loaded).fields['plan_mode'], 'scenarios')
        self.assertIn('Expected profit: Unknown', loaded)

    def test_scenario_attestations_require_matching_recipe_and_show_downside(self):
        html = self.post(self.form, workflow='crafting', plan_mode='scenarios', recipe='synthetic-bar', product='2',
                         target='1', selling='10', tax='0', sale_fee='0', fee_source='SYNTHETIC', p0='10', p1='2',
                         craft_fee='0', probability_evidence='SYNTHETIC deterministic fixture',
                         consumption_evidence='SYNTHETIC full-input rule')
        self.assertIn('EVIDENCE_SCOPE', html)
        html = self.post(FormControls(html).fields, attempt_evidence_recipe='synthetic-bar')
        self.assertNotIn('role="alert"', html)
        self.assertIn('Worst modeled profit:', html)
        self.assertIn('Modeled probability of loss: 1/1', html)
        self.assertIn('not a guaranteed return', html)

    def test_ranking_filters_and_saved_plan_recompute_from_real_controls(self):
        html = self.post(self.form, workflow='crafting', plan_mode='rank', recipe='synthetic-bar', product='2',
                         target='1', selling='100', tax='0', sale_fee='0', fee_source='SYNTHETIC', p0='10', p1='2',
                         craft_fee='0', rank_budget='1000', rank_age='10000000', rank_professions='SYNTHETIC smith',
                         profession0='SYNTHETIC smith', profession_ref0='SYNTHETIC classification',
                         requirements_ok0='\n'.join(self.c.recipes[0].requirements))
        self.assertNotIn('role="alert"', html)
        self.assertIn('1 routes pass the selected filters', html)
        self.assertIn('sell_through_unknown', html)
        saved = self.post(FormControls(html).fields, action='save', plan_name='ranked')
        self.assertIn('Saved locally at revision 1', saved)
        loaded = self.post(FormControls(saved).fields, action='load')
        self.assertIn('1 routes pass the selected filters', loaded)
        stale = self.post(FormControls(loaded).fields, rank_age='0')
        self.assertIn('0 routes pass the selected filters', stale)
        self.assertIn('stale_future_or_unknown_price_age', stale)

    def test_ranking_budget_and_requirements_never_default_to_approval(self):
        html = self.post(self.form, workflow='crafting', plan_mode='rank', recipe='synthetic-bar', product='2',
                         target='1', selling='100', tax='0', sale_fee='0', fee_source='SYNTHETIC', p0='10', p1='2',
                         craft_fee='0', rank_budget='0', rank_age='10000000')
        self.assertNotIn('role="alert"', html)
        self.assertIn('unknown_profession:synthetic-bar', html)
        self.assertIn('over_budget', html)

    def ledger_post(self, form, **changes):
        with urlopen(Request(self.url + '/ledger', data=urlencode(dict(form, **changes)).encode())) as response:
            return response.read().decode()

    def ledger_form(self):
        with urlopen(self.url + '/ledger') as response:
            return FormControls(response.read().decode()).fields

    def test_actual_journal_preview_save_export_and_reopen(self):
        from aioncrafter.ledger import decode_journal, evaluate_journal
        form = self.ledger_form()
        html = self.ledger_post(form, action='preview_record', journal_name='SYNTHETIC actuals',
                                market='test-server', currency='TEST', occurred='2026-10-04T10:00:00Z',
                                record_ref='SYNTHETIC purchase', record_kind='purchase', record_item='0',
                                record_quantity='3', paid_total='10')
        self.assertIn('unsaved preview', html)
        html = self.ledger_post(FormControls(html).fields, action='preview_record', record_kind='craft',
                                record_ref='SYNTHETIC actual craft', consumed0='3', produced2='2', paid_fee='2')
        html = self.ledger_post(FormControls(html).fields, action='preview_record', record_kind='sale',
                                record_ref='SYNTHETIC actual sale', record_item='2', record_quantity='1',
                                received='10', paid_fee='1')
        self.assertIn('Realized profit / loss: 3.00', html)
        self.assertIn('Net cash flow during this journal: -3.00', html)
        saved = self.ledger_post(FormControls(html).fields, action='save')
        self.assertIn('Journal saved locally at revision 1', saved)
        payload = self.ledger_post(FormControls(saved).fields, action='export')
        journal = decode_journal(payload.encode(), self.c)
        self.assertEqual(evaluate_journal(journal, self.c).realized_profit, 300)
        loaded = self.ledger_post(self.ledger_form(), action='load', journal_name='SYNTHETIC actuals')
        self.assertIn('Realized profit / loss: 3.00', loaded)
        self.assertEqual(decode_journal(FormControls(loaded).fields['journal_payload'].encode(), self.c), journal)
        imported = self.ledger_post(self.ledger_form(), action='import', import_data=payload)
        copied = self.ledger_post(FormControls(imported).fields, action='save', journal_name='SYNTHETIC actuals copy')
        self.assertIn('Journal saved locally at revision 1', copied)

    def test_actual_journal_bad_input_preserves_preview_and_does_not_crash(self):
        from aioncrafter.ledger import decode_journal
        html = self.ledger_post(self.ledger_form(), action='preview_record', journal_name='SYNTHETIC preview',
                                market='test-server', currency='TEST', occurred='2026-10-04T10:00:00Z',
                                record_ref='SYNTHETIC <receipt>', record_kind='opening', record_item='0',
                                record_quantity='3', paid_total='')
        before = FormControls(html).fields['journal_payload']
        bad = self.ledger_post(FormControls(html).fields, action='preview_record', record_kind='sale',
                               record_quantity='4', received='10', paid_fee='0')
        self.assertIn('INSUFFICIENT_STOCK', bad)
        self.assertEqual(FormControls(bad).fields['journal_payload'], before)
        self.assertIn('&lt;receipt&gt;', html)
        broken = self.ledger_post(self.ledger_form(), action='save', journal_payload='{broken')
        self.assertIn('Actual records', broken)
        self.assertNotIn('Journal saved', broken)
        self.assertEqual(len(decode_journal(before.encode(), self.c).records), 1)

    def test_actual_journal_requires_csrf_before_saving(self):
        html = self.ledger_post(self.ledger_form(), action='save', csrf='wrong')
        self.assertIn('CSRF', html)
        self.assertNotIn('Journal saved', html)

    def test_reference_id_replay_is_idempotent_but_changed_record_is_atomic(self):
        form = FormControls(self.post(self.form)).fields
        before = self.observations(form)
        replay = self.post(form, action='references', reference_data=dumps((before[0],)))
        self.assertIn('Reference import validated', replay)
        self.assertEqual(self.observations(FormControls(replay).fields), before)
        valid = replace(before[1], observation_id='new-vendor', price_type=PriceType.VENDOR_PURCHASE)
        for changed in (replace(before[0], unit_price='99'),
                        replace(before[0], fetched_at='2026-10-05T10:00:00Z'),
                        replace(before[0], price_type=PriceType.SNAPSHOT)):
            html = self.post(form, action='references', reference_data=dumps((valid, changed)))
            self.assertIn('REFERENCE_ID', html)
            self.assertNotIn('Reference import validated', html)
            self.assertEqual(self.observations(FormControls(html).fields), before)

    def test_wrong_scope_type_and_rights_imports_preserve_saved_plan(self):
        saved = self.post(self.form, action='save', plan_name='unchanged')
        form = FormControls(saved).fields
        before = self.observations(form)
        base = replace(before[0], observation_id='rejected-import', price_type=PriceType.SNAPSHOT)
        unverified = json.loads(dumps((base,)))
        unverified[0]['provenance']['rights_status'] = 'unverified'
        cases = ((dumps((replace(base, identity=replace(base.identity, market=replace(base.identity.market, market_id='other'))),)), 'REFERENCE_SCOPE'),
                 (dumps((replace(base, price_type=PriceType.VENDOR_SELL_BACK),)), 'REFERENCE_TYPE'),
                 (json.dumps(unverified), 'PROVENANCE'))
        for payload, code in cases:
            html = self.post(form, action='references', reference_data=payload)
            self.assertIn(code, html)
            self.assertEqual(self.observations(FormControls(html).fields), before)
        with PlanStore(self.path) as store:
            revision, plan = store.load('unchanged', self.c)
            self.assertEqual(revision, 1)
            self.assertEqual(plan.observations, before)

    def test_zero_reference_is_known_and_missing_reference_is_unavailable(self):
        base = replace(observation(), observation_id='zero-snapshot', price_type=PriceType.SNAPSHOT,
                       unit_price='0', observed_at=None)
        html = self.post(self.form, action='references', reference_data=dumps((base,)))
        self.assertIn('Snapshot · age unknown', html)
        html = self.post(FormControls(html).fields)
        self.assertIn('Total: 0.00', html)
        missing = replace(base, observation_id='missing-snapshot', unit_price=None)
        html = self.post(FormControls(html).fields, action='references', reference_data=dumps((missing,)))
        self.assertIn('Snapshot · unavailable · age unknown', html)
        html = self.post(FormControls(html).fields)
        self.assertIn('Total: Incomplete', html)
