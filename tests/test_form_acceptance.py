"""End-to-end local HTTP forms; does not claim browser rendering acceptance."""
from dataclasses import replace
from http.server import HTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import tempfile
import unittest

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
